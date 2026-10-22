'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkCjkFriendly from 'remark-cjk-friendly'

interface DigestResult {
  video_id: string
  digest: string
  model: string
  title: string
  channel: string
  published: string
  thumbnail: string
  url: string
  tags: string[]
}

interface ApiError {
  error: string
  message: string
}

type DetailLevel = 'brief' | 'standard' | 'detailed'

// Obsidian設定
const DEFAULT_VAULT_NAME = 'BrainDump'
const DEFAULT_FOLDER_PATH = 'YouTube要約'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DigestResult | null>(null)
  const [copied, setCopied] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [detailLevel, setDetailLevel] = useState<DetailLevel>('detailed')
  const [vaultName, setVaultName] = useState(DEFAULT_VAULT_NAME)
  const [folderPath, setFolderPath] = useState(DEFAULT_FOLDER_PATH)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [editableTags, setEditableTags] = useState<string[]>([])
  const [newTag, setNewTag] = useState('')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'dark' | 'light' | null
    if (savedTheme) {
      setTheme(savedTheme)
      document.documentElement.setAttribute('data-theme', savedTheme)
    }
    const savedVault = localStorage.getItem('vaultName')
    if (savedVault) {
      setVaultName(savedVault)
    }
    const savedFolder = localStorage.getItem('folderPath')
    if (savedFolder) {
      setFolderPath(savedFolder)
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  const saveVaultName = (name: string) => {
    setVaultName(name)
    localStorage.setItem('vaultName', name)
  }

  const saveFolderPath = (path: string) => {
    setFolderPath(path)
    localStorage.setItem('folderPath', path)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)
    setSaveMessage(null)

    try {
      const response = await fetch(`${API_URL}/api/digest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, detail_level: detailLevel }),
      })

      if (!response.ok) {
        const errorData: { detail: ApiError } = await response.json()
        throw new Error(errorData.detail?.message || 'エラーが発生しました')
      }

      const data: DigestResult = await response.json()
      setResult(data)
      setEditableTags(data.tags || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setLoading(false)
    }
  }

  const removeTag = (index: number) => {
    setEditableTags(prev => prev.filter((_, i) => i !== index))
  }

  const addTag = () => {
    const tag = newTag.trim().replace(/\s+/g, '') // スペース除去
    if (tag && !editableTags.includes(tag)) {
      setEditableTags(prev => [...prev, tag])
      setNewTag('')
    }
  }

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addTag()
    }
  }

  const copyToClipboard = async () => {
    if (!result?.digest) return

    try {
      await navigator.clipboard.writeText(result.digest)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      const textArea = document.createElement('textarea')
      textArea.value = result.digest
      textArea.style.position = 'fixed'
      textArea.style.left = '-9999px'
      document.body.appendChild(textArea)
      textArea.select()
      try {
        document.execCommand('copy')
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch {
        console.error('コピーに失敗しました')
      }
      document.body.removeChild(textArea)
    }
  }

  const generateFrontmatter = () => {
    if (!result) return ''
    const created = new Date().toISOString().split('T')[0]
    const tagsYaml = editableTags.length > 0
      ? `tags:\n${editableTags.map(t => `  - ${t}`).join('\n')}`
      : ''

    return `---
title: "${result.title}"
channel: "${result.channel}"
published: ${result.published || 'unknown'}
url: ${result.url}
thumbnail: ${result.thumbnail}
model: ${result.model}
created: ${created}
${tagsYaml}
---

`
  }

  const sanitizeFilename = (text: string): string => {
    // 最初の見出しからタイトルを抽出
    const match = text.match(/^# (.+)$/m)
    let title = match ? match[1].trim() : 'untitled'
    // ファイル名に使えない文字を除去
    title = title.replace(/[<>:"/\\|?*]/g, '')
    return title.slice(0, 50)
  }

  const saveToObsidian = () => {
    if (!result) return

    setSaving(true)
    setSaveMessage(null)

    try {
      // フロントマター + コンテンツ
      const frontmatter = generateFrontmatter()
      const fullContent = frontmatter + result.digest

      // ファイル名生成
      const title = sanitizeFilename(result.digest)
      const dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '')
      const filename = `${title}_${dateStr}`

      // Vault内のファイルパス
      const filePath = folderPath ? `${folderPath}/${filename}` : filename

      // Obsidian URI生成
      const uri = `obsidian://new?vault=${encodeURIComponent(vaultName)}&file=${encodeURIComponent(filePath)}&content=${encodeURIComponent(fullContent)}`

      // Obsidianを開く
      window.location.href = uri

      setSaveMessage(`Obsidianで開きました: ${filename}.md`)
    } catch (err) {
      setSaveMessage(err instanceof Error ? err.message : '保存に失敗しました')
    } finally {
      setSaving(false)
    }
  }

  const thumbnailUrl = result?.thumbnail ||
    (result?.video_id ? `https://img.youtube.com/vi/${result.video_id}/maxresdefault.jpg` : null)

  return (
    <div className="app-container">
      <header className="header">
        <button className="theme-toggle" onClick={toggleTheme} title="テーマ切り替え">
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <h1 className="logo">YouTube要約</h1>
        <p className="tagline">動画の内容を、読み物として</p>
      </header>

      <main className="main-content">
        <section className="search-section">
          <form className="search-form" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <input
                type="text"
                className="url-input"
                placeholder="YouTube URLを入力..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={loading}
              />
              <button type="submit" className="submit-btn" disabled={loading || !url.trim()}>
                {loading ? '解析中...' : '解説を生成'}
              </button>
            </div>
            <div className="options-bar">
              <div className="option-group">
                <span className="option-label">詳細度</span>
                <select
                  className="detail-select"
                  value={detailLevel}
                  onChange={(e) => setDetailLevel(e.target.value as DetailLevel)}
                  disabled={loading}
                >
                  <option value="brief">簡潔</option>
                  <option value="standard">標準</option>
                  <option value="detailed">詳細</option>
                </select>
              </div>
            </div>
          </form>
        </section>

        {error && <div className="error-message">{error}</div>}

        {loading && (
          <div className="loading-state">
            <div className="loading-spinner" />
            <p className="loading-text">動画を解析中...</p>
            <p className="loading-subtext">字幕の取得と解説の生成には少し時間がかかります</p>
          </div>
        )}

        {result && (
          <article className="result-card">
            {thumbnailUrl && (
              <div className="hero-section">
                <img
                  src={thumbnailUrl}
                  alt=""
                  className="hero-thumbnail"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      `https://img.youtube.com/vi/${result.video_id}/hqdefault.jpg`
                  }}
                  onLoad={(e) => {
                    // 高画質のサムネイルが無い動画では、YouTube が 120x90 の灰色の仮の絵を返す
                    const img = e.target as HTMLImageElement
                    if (img.naturalWidth <= 120 && !img.src.endsWith('/hqdefault.jpg')) {
                      img.src = `https://img.youtube.com/vi/${result.video_id}/hqdefault.jpg`
                    }
                  }}
                />
                <div className="hero-overlay" />
                <div className="hero-content">
                  <h2 className="video-title">{result.title || '動画タイトル'}</h2>
                  <div className="video-meta">
                    {result.channel && (
                      <span className="meta-item">
                        <span className="meta-label">Ch.</span> {result.channel}
                      </span>
                    )}
                    {result.published && (
                      <span className="meta-item">
                        <span className="meta-label">公開</span> {result.published}
                      </span>
                    )}
                    <span className="meta-item">
                      <span className="meta-label">モデル</span> {result.model}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div className="tags-section">
              {editableTags.map((tag, i) => (
                <span key={i} className="tag editable" onClick={() => removeTag(i)}>
                  #{tag}
                  <span className="tag-remove">×</span>
                </span>
              ))}
              <input
                type="text"
                className="tag-input"
                placeholder="タグ追加..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyDown={handleTagKeyDown}
                onBlur={addTag}
              />
            </div>

            <div className="action-bar">
              <span className="action-info">
                {result.digest.length.toLocaleString()} 文字
              </span>
              <div className="action-buttons">
                <button className="action-btn secondary" onClick={copyToClipboard}>
                  {copied ? 'コピー済み!' : 'コピー'}
                </button>
                <button
                  className="action-btn primary"
                  onClick={saveToObsidian}
                  disabled={saving}
                >
                  {saving ? '保存中...' : 'Obsidianに保存'}
                </button>
              </div>
            </div>

            {saveMessage && (
              <div className={`save-message ${saveMessage.includes('失敗') ? 'error' : ''}`}>
                {saveMessage}
              </div>
            )}

            <div className="digest-content">
              <ReactMarkdown remarkPlugins={[remarkCjkFriendly]}>{result.digest}</ReactMarkdown>
            </div>
          </article>
        )}

        <section className="settings-section">
          <div className="settings-card">
            <div className="settings-row">
              <span className="settings-label">Vault名</span>
              <input
                type="text"
                className="settings-input"
                value={vaultName}
                onChange={(e) => saveVaultName(e.target.value)}
                placeholder="ObsidianのVault名"
              />
            </div>
            <div className="settings-row">
              <span className="settings-label">フォルダ</span>
              <input
                type="text"
                className="settings-input"
                value={folderPath}
                onChange={(e) => saveFolderPath(e.target.value)}
                placeholder="保存先フォルダ（例: YouTube要約）"
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
