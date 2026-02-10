import { CheckCircle, FlaskConical, Quote } from 'lucide-react'

type BPPlusContentProps = {
  content: string
}

const TAGS = {
  essence: '[СУТЬ]',
  benefits: '[ПОЛЬЗА]',
  recommendation: '[РЕКОМЕНДАЦИЯ]',
}

const extractSection = (text: string, startTag: string, endTags: string[]) => {
  const startIndex = text.indexOf(startTag)
  if (startIndex === -1) return ''
  const start = startIndex + startTag.length
  const rest = text.slice(start)
  let end = rest.length
  endTags.forEach((tag) => {
    const idx = rest.indexOf(tag)
    if (idx !== -1 && idx < end) end = idx
  })
  return rest.slice(0, end).trim()
}

const parseBPPlusContent = (raw: string) => {
  const text = raw.replace(/\r\n/g, '\n').trim()
  const firstTagIndex = Math.min(
    ...[TAGS.essence, TAGS.benefits, TAGS.recommendation]
      .map((tag) => text.indexOf(tag))
      .filter((idx) => idx >= 0),
  )
  const introBlock = firstTagIndex >= 0 ? text.slice(0, firstTagIndex).trim() : text
  const introLines = introBlock
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)

  const quotes = introLines
    .filter((line) => line.startsWith('>'))
    .map((line) => line.replace(/^>\s?/, '').trim())
  const introduction = introLines.filter((line) => !line.startsWith('>')).join('\n')

  const essence = extractSection(text, TAGS.essence, [TAGS.benefits, TAGS.recommendation])
  const benefitsBlock = extractSection(text, TAGS.benefits, [TAGS.recommendation])
  const recommendation = extractSection(text, TAGS.recommendation, [])

  const benefits = benefitsBlock
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .flatMap((line) => {
      if (line.startsWith('-')) return [line.replace(/^-+\s*/, '')]
      if (line.startsWith('✅')) return [line.replace(/^✅\s*/, '')]
      return line.includes(' - ') ? line.split(' - ').map((item) => item.trim()) : [line]
    })
    .map((item) => item.replace(/^[-•]\s*/, '').trim())
    .filter(Boolean)

  return {
    introduction: introduction.replace(/\[(СУТЬ|ПОЛЬЗА|РЕКОМЕНДАЦИЯ)\]/gi, '').trim(),
    quotes,
    essence: essence.replace(/\[(СУТЬ|ПОЛЬЗА|РЕКОМЕНДАЦИЯ)\]/gi, '').trim(),
    benefits,
    recommendation: recommendation.replace(/\[(СУТЬ|ПОЛЬЗА|РЕКОМЕНДАЦИЯ)\]/gi, '').trim(),
  }
}

export default function BPPlusContent({ content }: BPPlusContentProps) {
  const parsed = parseBPPlusContent(content || '')
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <span className="text-sm uppercase tracking-widest text-[#D8B46C]">Мнение BioPeptidePlus</span>
        <span className="px-3 py-1 rounded-full bg-gradient-to-r from-[#D8B46C] to-[#F7E4B2] text-xs font-semibold text-gray-900">
          Экспертный разбор
        </span>
      </div>

      {parsed.introduction && (
        <div className="space-y-3 whitespace-pre-line text-gray-200 leading-relaxed">
          {parsed.introduction}
        </div>
      )}

      {parsed.quotes.length > 0 && (
        <div className="space-y-3">
          {parsed.quotes.map((quote, idx) => (
            <div
              key={`quote-${idx}`}
              className="relative border-l-4 border-[#D8B46C] pl-5 text-lg text-gray-100 font-medium"
            >
              <Quote className="absolute -left-2 -top-2 w-8 h-8 text-[#D8B46C]/20" />
              {quote}
            </div>
          ))}
        </div>
      )}

      {parsed.essence && (
        <div className="rounded-2xl bg-[#0E2A47] border border-[#1F4F80] p-5 shadow-xl">
          <div className="flex items-center gap-2 text-[#8BC2FF] font-semibold mb-2">
            <FlaskConical className="w-5 h-5 text-blue-400" />
            <span>Суть исследования</span>
          </div>
          <p className="text-gray-200 leading-relaxed whitespace-pre-line">{parsed.essence}</p>
        </div>
      )}

      {parsed.benefits.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-[#F7E4B2]">Польза</h3>
          <div className="grid gap-3 md:grid-cols-2">
            {parsed.benefits.map((item, idx) => (
              <div
                key={`benefit-${idx}`}
                className="rounded-2xl border border-[#D8B46C] bg-[#2C2315] p-4 text-gray-100"
              >
                <div className="flex items-start gap-2">
                  <CheckCircle className="w-5 h-5 text-[#D8B46C]" />
                  <span>{item}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {parsed.recommendation && (
        <div className="rounded-2xl border border-[#D8B46C] bg-gradient-to-r from-[#2C2315] to-[#3A2E1B] p-5">
          <h3 className="text-lg font-semibold text-[#F7E4B2] mb-2">Рекомендация</h3>
          <p className="text-gray-100 leading-relaxed whitespace-pre-line">{parsed.recommendation}</p>
          <p className="mt-4 text-[#F7E4B2]">— Команда BioPeptidePlus</p>
        </div>
      )}

      <div className="pt-4">
        <button
          className="px-6 py-3 rounded-full bg-[#0ABAB5] text-gray-900 font-semibold shadow-lg hover:scale-[1.02] transition"
          onClick={() => {
            // TODO: Вставить реальный ID, я заменю его позже перед финальным запуском.
            const ym = (window as typeof window & { ym?: (...args: unknown[]) => void }).ym
            if (typeof ym === 'function') {
              ym(99999999, 'reachGoal', 'phone_click')
            }
          }}
        >
          Консультация
        </button>
      </div>
    </div>
  )
}
