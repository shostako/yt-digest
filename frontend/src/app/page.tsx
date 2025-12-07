'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

interface DigestResult {
  video_id: string
  digest: string
  transcript_language: string
  is_auto_generated: boolean
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

const DEFAULT_OUTPUT_PATH = 'C:\\Users\\shost\\Documents\\BrainDump\\YouTube要約'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<DigestResult | null>(null)
  const [copied, setCopied] = useState(false)
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [detailLevel, setDetailLevel] = useState<DetailLevel>('detailed')
  const [outputPath, setOutputPath] = useState(DEFAULT_OUTPUT_PATH)
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
    const savedPath = localStorage.getItem('outputPath')
    if (savedPath) {
      setOutputPath(savedPath)
    }
  }, [])

  const toggleTheme = () => {
    const newTheme = theme === 'dark' ? 'light' : 'dark'
    setTheme(newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }

  const saveOutputPath = (path: string) => {
    setOutputPath(path)
    localStorage.setItem('outputPath', path)
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

  const saveToObsidian = async () => {
    if (!result) return

    setSaving(true)
    setSaveMessage(null)

    try {
      const response = await fetch(`${API_URL}/api/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          video_id: result.video_id,
          content: result.digest,
          output_path: outputPath,
          title: result.title,
          channel: result.channel,
          published: result.published,
          url: result.url,
          thumbnail: result.thumbnail,
          tags: editableTags,
          model: result.model,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || '保存に失敗しました')
      }

      const data = await response.json()
      setSaveMessage(`保存完了: ${data.filename}`)
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
                    <span className="meta-item">
                      <span className="meta-label">言語</span>
                      {result.transcript_language}
                      {result.is_auto_generated && ' (自動)'}
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
              <ReactMarkdown>{result.digest}</ReactMarkdown>
            </div>
          </article>
        )}

        <section className="settings-section">
          <div className="settings-card">
            <div className="settings-row">
              <span className="settings-label">出力先</span>
              <input
                type="text"
                className="settings-input"
                value={outputPath}
                onChange={(e) => saveOutputPath(e.target.value)}
                placeholder="Obsidian Vaultのパス"
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
