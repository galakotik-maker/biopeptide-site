import { useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { journalData } from '../data/journalData'

type JournalPost = {
  id?: string
  title?: string
  description?: string
  summary?: string
  created_at?: string
  date?: string
}

const SKELETON_ITEMS = Array.from({ length: 6 }, (_, index) => index)

const formatDate = (value?: string) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

const fetchJournalPosts = async (): Promise<JournalPost[]> => {
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY
  if (!supabaseUrl || !supabaseKey) {
    return []
  }

  const endpoint = `${supabaseUrl.replace(/\/$/, '')}/rest/v1/journal_posts?select=id,title,description,summary,created_at,date&order=created_at.desc&limit=12`
  const response = await fetch(endpoint, {
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
    },
  })
  if (!response.ok) {
    return []
  }
  return response.json()
}

export default function Journal() {
  const [posts, setPosts] = useState<JournalPost[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    fetchJournalPosts()
      .then((data) => {
        if (mounted) {
          const merged = [...journalData, ...data]
          setPosts(merged)
        }
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  const showSkeletons = useMemo(() => !loading && posts.length === 0, [loading, posts])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <p className="text-sm uppercase tracking-widest text-[#0ABAB5] font-semibold">
            BioPeptidePlus Journal
          </p>
          <h1 className="text-3xl md:text-4xl font-bold text-white mt-3">
            Новости в Биохакинге
          </h1>
          <p className="text-gray-400 mt-4 max-w-2xl mx-auto">
            Сухие факты, практические выводы и фокус на научной достоверности.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {loading && (
            <div className="col-span-full text-center text-gray-400">
              Загружаем свежие публикации...
            </div>
          )}

          {showSkeletons &&
            SKELETON_ITEMS.map((item) => (
              <div
                key={`skeleton-${item}`}
                className="bg-slate-800/60 border border-slate-700 rounded-2xl p-6 shadow-2xl animate-pulse"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="h-3 w-16 rounded-full bg-[#0ABAB5]/40" />
                  <span className="h-3 w-20 rounded-full bg-slate-600/60" />
                </div>
                <div className="h-5 w-3/4 rounded-full bg-slate-600/60 mb-4" />
                <div className="h-3 w-full rounded-full bg-slate-700/70 mb-2" />
                <div className="h-3 w-5/6 rounded-full bg-slate-700/70" />
              </div>
            ))}

          {!loading &&
            posts.map((article) => (
              <div
                key={article.id || article.title}
                className="bg-slate-800/80 border border-slate-700 rounded-2xl p-6 shadow-2xl hover:-translate-y-1 hover:scale-[1.01] transition-all duration-300 ease-in-out"
              >
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs uppercase tracking-widest text-[#0ABAB5]">
                    Journal
                  </span>
                  <span className="text-xs text-gray-400">
                    {formatDate(article.date || article.created_at)}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">
                  {article.title || 'Без названия'}
                </h3>
                <div className="text-gray-300 leading-relaxed space-y-2">
                  <ReactMarkdown
                    components={{
                      h2: (props) => <h2 className="text-lg font-semibold text-white mt-4 mb-2" {...props} />,
                      strong: (props) => <strong className="text-white font-semibold" {...props} />,
                      ul: (props) => <ul className="list-disc pl-5 space-y-1" {...props} />,
                      li: (props) => <li className="text-gray-300" {...props} />,
                      p: (props) => <p className="text-gray-300 leading-relaxed" {...props} />,
                    }}
                  >
                    {article.description || article.summary || 'Описание отсутствует.'}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
