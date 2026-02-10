import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { journalData } from '../data/journalData'
import BPPlusContent from '../components/BPPlusContent'

type JournalArticle = {
  id?: string
  title?: string
  description?: string
  summary?: string
  content_lite?: string
  image_url?: string
  created_at?: string
  date?: string
}

const PLACEHOLDER_IMAGE =
  'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80'

const formatDate = (value?: string) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: '2-digit',
  })
}

const cleanText = (value?: string) => {
  if (!value) return ''
  return value
    .replace(/\[(СУТЬ|ПОЛЬЗА|РЕКОМЕНДАЦИЯ)\]/gi, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}

const toTaggedFormat = (value?: string) => {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed.startsWith('{') || !trimmed.includes('introduction')) return value
  const extractField = (key: string) => {
    const pattern = new RegExp(
      `[\\'"]${key}[\\'"]\\s*:\\s*([\\s\\S]*?)(?=,\\s*[\\'"](introduction|essence|conclusion)[\\'"]\\s*:|\\}$)`,
      'i',
    )
    const match = trimmed.match(pattern)
    if (!match) return ''
    let raw = match[1].trim().replace(/,$/, '')
    if ((raw.startsWith("'") && raw.endsWith("'")) || (raw.startsWith('"') && raw.endsWith('"'))) {
      raw = raw.slice(1, -1)
    }
    return raw.trim()
  }
  const introduction = extractField('introduction')
  const essence = extractField('essence')
  const conclusion = extractField('conclusion')
  const parts = []
  if (introduction) parts.push(introduction)
  if (essence) parts.push('[СУТЬ]\n' + essence)
  if (conclusion) parts.push('[РЕКОМЕНДАЦИЯ]\n' + conclusion)
  return parts.join('\n\n').trim()
}

const fetchArticle = async (id: string): Promise<JournalArticle | null> => {
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY
  if (!supabaseUrl || !supabaseKey) return null

  const endpoint = `${supabaseUrl.replace(/\/$/, '')}/rest/v1/journal_posts?id=eq.${id}&select=id,title,description,summary,content_lite,image_url,created_at,date&limit=1`
  const response = await fetch(endpoint, {
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
    },
  })
  if (!response.ok) return null
  const data = await response.json()
  return data?.[0] ?? null
}

export default function ArticlePage() {
  const { id } = useParams()
  const [article, setArticle] = useState<JournalArticle | null>(null)
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<'expert' | 'lite' | 'bp'>('expert')

  useEffect(() => {
    let mounted = true
    if (!id) {
      setLoading(false)
      return
    }
    fetchArticle(id)
      .then((data) => {
        if (!mounted) return
        if (data) {
          setArticle(data)
          return
        }
        const local = journalData.find((item) => item.id === id) || null
        setArticle(local)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [id])

  const heroImage = article?.image_url || PLACEHOLDER_IMAGE
  const rawExpert = toTaggedFormat(article?.description || article?.summary || '')
  const cleanExpert = cleanText(rawExpert)
  const liteContent = article?.content_lite || article?.summary || ''
  const hasBpTags = /(\[СУТЬ\]|\[ПОЛЬЗА\]|\[РЕКОМЕНДАЦИЯ\])/i.test(rawExpert)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <Link to="/journal" className="text-sm text-[#0ABAB5] hover:underline">
          ← К журналу
        </Link>

        {loading && <div className="text-gray-400 mt-6">Загружаем статью...</div>}

        {!loading && !article && (
          <div className="text-gray-400 mt-6">Статья не найдена.</div>
        )}

        {!loading && article && (
          <div className="mt-6">
            <div className="rounded-3xl overflow-hidden border border-slate-700 shadow-2xl mb-8">
              <img src={heroImage} alt={article.title || 'BioPeptidePlus'} className="w-full h-64 object-cover" />
            </div>

            <div className="flex items-center justify-between mb-4">
              <span className="text-xs uppercase tracking-widest text-[#0ABAB5]">BP+ View</span>
              <span className="text-xs text-gray-400">
                {formatDate(article.date || article.created_at)}
              </span>
            </div>

            <h1 className="text-3xl md:text-4xl font-bold text-white mb-6">
              {article.title || 'Без названия'}
            </h1>

            <div className="flex gap-3 mb-8 flex-wrap">
              <button
                className={`px-4 py-2 rounded-full text-sm font-semibold ${
                  view === 'expert' ? 'bg-[#0ABAB5] text-gray-900' : 'bg-slate-800 text-gray-300'
                }`}
                onClick={() => setView('expert')}
              >
                Expert
              </button>
              <button
                className={`px-4 py-2 rounded-full text-sm font-semibold ${
                  view === 'bp' ? 'bg-[#D8B46C] text-gray-900' : 'bg-slate-800 text-gray-300'
                }`}
                onClick={() => setView('bp')}
              >
                BP+ View
              </button>
              <button
                className={`px-4 py-2 rounded-full text-sm font-semibold ${
                  view === 'lite' ? 'bg-[#0ABAB5] text-gray-900' : 'bg-slate-800 text-gray-300'
                }`}
                onClick={() => setView('lite')}
              >
                Lite
              </button>
            </div>

            {view === 'bp' && (
              <div className="text-gray-300 leading-relaxed space-y-4">
                {hasBpTags ? (
                  <BPPlusContent content={rawExpert} />
                ) : (
                  <div className="text-gray-400">Контент готовится...</div>
                )}
              </div>
            )}

            {view === 'lite' && (
              <div className="text-gray-300 leading-relaxed space-y-3">
                <ReactMarkdown
                  components={{
                    strong: (props) => <strong className="text-white font-semibold" {...props} />,
                    ul: (props) => <ul className="list-disc pl-5 space-y-1" {...props} />,
                    li: (props) => <li className="text-gray-300" {...props} />,
                    p: (props) => <p className="text-gray-300 leading-relaxed" {...props} />,
                  }}
                >
                  {liteContent || 'Lite-версия не найдена.'}
                </ReactMarkdown>
              </div>
            )}

            {view === 'expert' && (
              <ReactMarkdown
                components={{
                  h2: (props) => <h2 className="text-lg font-semibold text-white mt-4 mb-2" {...props} />,
                  strong: (props) => <strong className="text-white font-semibold" {...props} />,
                  ul: (props) => <ul className="list-disc pl-5 space-y-1" {...props} />,
                  li: (props) => <li className="text-gray-300" {...props} />,
                  p: (props) => <p className="text-gray-300 leading-relaxed" {...props} />,
                }}
              >
                {cleanExpert || 'Expert-версия не найдена.'}
              </ReactMarkdown>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
