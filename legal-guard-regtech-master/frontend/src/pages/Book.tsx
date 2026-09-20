import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

type PeptideCard = {
  name: string
  slug: string
  pmids?: string[]
  wada?: string
  dosage?: string
  fda_2026?: string
  content?: string
}

type Chapter = {
  number: number
  title: string
  slug: string
  intro?: string
  peptides?: PeptideCard[]
}

type Protocol = {
  number?: string | number
  title: string
  slug: string
  emoji?: string
  duration?: string
  target?: string
  content?: string
  composition?: string
  results?: string
  case_study?: string
  contraindications?: string
}

type BookData = {
  title: string
  subtitle?: string
  chapters: Chapter[]
  protocols?: Protocol[]
  stats?: {
    total_peptides?: number
    total_chapters?: number
    total_protocols?: number
    total_pmids?: number
  }
}

export default function Book() {
  const [book, setBook] = useState<BookData | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [openChapters, setOpenChapters] = useState<Set<string>>(new Set())
  const [activeId, setActiveId] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    fetch('/book_web.json')
      .then((response) => {
        if (!response.ok) throw new Error('book_web.json not found')
        return response.json()
      })
      .then((data: BookData) => {
        if (!mounted) return
        setBook(data)
      })
      .catch(() => {
        if (mounted) setBook(null)
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })
    return () => {
      mounted = false
    }
  }, [])

  const chapters = useMemo(() => {
    if (!book) return []
    const needle = query.trim().toLowerCase()
    if (!needle) return book.chapters
    return book.chapters
      .map((chapter) => {
        const titleHit = chapter.title.toLowerCase().includes(needle)
        const peptides = (chapter.peptides || []).filter((peptide) =>
          peptide.name.toLowerCase().includes(needle),
        )
        if (titleHit || peptides.length > 0) {
          return { ...chapter, peptides: titleHit ? chapter.peptides || [] : peptides }
        }
        return null
      })
      .filter((chapter): chapter is Chapter => Boolean(chapter))
  }, [book, query])

  useEffect(() => {
    if (query.trim()) {
      setOpenChapters(new Set(chapters.map((chapter) => chapter.slug)))
    }
  }, [query, chapters])

  useEffect(() => {
    if (!book) return
    const hash = decodeURIComponent(window.location.hash.replace(/^#/, ''))
    if (!hash) return
    const chapter = book.chapters.find(
      (item) => item.slug === hash || (item.peptides || []).some((peptide) => peptide.slug === hash),
    )
    if (chapter) {
      setOpenChapters((prev) => new Set(prev).add(chapter.slug))
      setActiveId(hash)
      requestAnimationFrame(() => {
        document.getElementById(hash)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    }
  }, [book])

  const scrollTo = (id: string, chapterSlug?: string) => {
    setActiveId(id)
    if (chapterSlug) {
      setOpenChapters((prev) => new Set(prev).add(chapterSlug))
    }
    const node = document.getElementById(id)
    if (node) node.scrollIntoView({ behavior: 'smooth', block: 'start' })
    window.history.replaceState(null, '', `#${id}`)
  }

  const toggleChapter = (slug: string) => {
    setOpenChapters((prev) => {
      const next = new Set(prev)
      if (next.has(slug)) next.delete(slug)
      else next.add(slug)
      return next
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-slate-950 text-gray-100 font-sans antialiased">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link to="/journal" className="text-sm text-[#0ABAB5] hover:underline">
          ← К журналу
        </Link>

        <div className="mt-6 mb-8">
          <p className="text-sm uppercase tracking-widest text-[#0ABAB5] font-semibold">
            Справочник 2026
          </p>
          <h1 className="text-3xl md:text-4xl font-bold text-white mt-3">
            {book?.title || 'Справочник по пептидам 2026'}
          </h1>
          {book?.subtitle && (
            <p className="text-gray-400 mt-3 text-lg">{book.subtitle}</p>
          )}
          <p className="text-gray-400 mt-4 max-w-3xl">
            Карточки пептидов для лабораторных исследований (Research Use Only). Не является
            медицинской инструкцией или схемой применения у людей.
          </p>
          {book?.stats && (
            <p className="text-xs text-gray-500 mt-3">
              {book.stats.total_peptides} карточек · {book.stats.total_chapters} глав ·{' '}
              {book.stats.total_pmids} PMID
            </p>
          )}
        </div>

        <div className="mb-8">
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Поиск по пептидам..."
            className="w-full md:w-96 rounded-xl bg-slate-800 border border-slate-700 px-4 py-3 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-[#0ABAB5]"
          />
        </div>

        {loading && <div className="text-gray-400">Загружаем справочник...</div>}
        {!loading && !book && (
          <div className="text-gray-400">Справочник скоро будет доступен.</div>
        )}

        {!loading && book && (
          <div className="grid lg:grid-cols-[260px_1fr] gap-8">
            <aside className="lg:sticky lg:top-8 h-fit rounded-2xl border border-slate-700 bg-slate-800/70 p-4">
              <div className="space-y-1 max-h-[70vh] overflow-y-auto pr-1">
                {chapters.map((chapter) => (
                  <div key={chapter.slug}>
                    <button
                      type="button"
                      onClick={() => {
                        toggleChapter(chapter.slug)
                        scrollTo(chapter.slug, chapter.slug)
                      }}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
                        activeId === chapter.slug
                          ? 'bg-[#0ABAB5]/15 text-[#0ABAB5]'
                          : 'text-gray-200 hover:bg-slate-700/80'
                      }`}
                    >
                      Гл. {chapter.number}. {chapter.title}
                    </button>
                    {openChapters.has(chapter.slug) && (chapter.peptides || []).length > 0 && (
                      <div className="ml-3 pl-3 border-l border-slate-600 space-y-0.5 py-1">
                        {(chapter.peptides || []).map((peptide) => (
                          <button
                            type="button"
                            key={peptide.slug}
                            onClick={() => scrollTo(peptide.slug, chapter.slug)}
                            className={`w-full text-left px-2 py-1.5 rounded-md text-xs ${
                              activeId === peptide.slug
                                ? 'bg-[#0ABAB5]/15 text-[#0ABAB5]'
                                : 'text-gray-400 hover:text-gray-100'
                            }`}
                          >
                            {peptide.name}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </aside>

            <main className="space-y-12">
              {chapters.map((chapter) => (
                <section key={chapter.slug} id={chapter.slug} className="scroll-mt-24">
                  <h2 className="text-2xl font-bold text-white mb-4 pb-2 border-b border-slate-700">
                    Глава {chapter.number}. {chapter.title}
                  </h2>
                  {chapter.intro && (
                    <p className="text-gray-300 leading-relaxed whitespace-pre-line mb-6">
                      {chapter.intro}
                    </p>
                  )}
                  <div className="space-y-6">
                    {(chapter.peptides || []).map((peptide) => (
                      <article
                        key={peptide.slug}
                        id={peptide.slug}
                        className="rounded-2xl border border-slate-700 bg-slate-800/80 p-5 md:p-6 scroll-mt-24"
                      >
                        <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                          <h3 className="text-lg md:text-xl font-semibold text-white">
                            {peptide.name}
                          </h3>
                          {peptide.slug === 'melanotan-ii' && (
                            <a
                              href="/research/melanotan-ii.html"
                              className="text-xs text-[#0ABAB5] hover:underline"
                            >
                              Научная карточка →
                            </a>
                          )}
                        </div>
                        {peptide.content && (
                          <p className="text-gray-300 leading-relaxed whitespace-pre-line">
                            {peptide.content}
                          </p>
                        )}
                        {peptide.fda_2026 && (
                          <div className="mt-4 rounded-xl border border-[#D8B46C]/40 bg-[#2C2315] p-3 text-sm text-[#F7E4B2] whitespace-pre-line">
                            {peptide.fda_2026}
                          </div>
                        )}
                        {peptide.pmids && peptide.pmids.length > 0 && (
                          <div className="mt-4 flex flex-wrap gap-1.5">
                            {peptide.pmids.map((pmid) => (
                              <a
                                key={pmid}
                                href={`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs px-2 py-0.5 rounded-full bg-[#0ABAB5]/15 text-[#0ABAB5] hover:bg-[#0ABAB5]/25"
                              >
                                PMID: {pmid}
                              </a>
                            ))}
                          </div>
                        )}
                      </article>
                    ))}
                  </div>
                </section>
              ))}
            </main>
          </div>
        )}
      </div>
    </div>
  )
}
