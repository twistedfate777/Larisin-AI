import { useState, useRef, useCallback } from 'react'
import { UploadSimple, X, CheckCircle, Warning, SpinnerGap, ArrowCounterClockwise } from '@phosphor-icons/react'
import { saveImage } from '../utils/storage'
import { submitImage } from '../utils/api'

const MAX_SIZE = 5 * 1024 * 1024 // 5 MB

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatCurrency(value) {
  return 'Rp ' + Math.round(value).toLocaleString('id-ID')
}

export default function UploadPage() {
  const [state, setState] = useState('idle') // idle | loading | preview | generating | result
  const [preview, setPreview] = useState(null)
  const [file, setFile] = useState(null)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [basePrice, setBasePrice] = useState('')
  const [stockDate, setStockDate] = useState('')
  const inputRef = useRef(null)

  const clearError = useCallback(() => {
    setTimeout(() => setError(null), 4000)
  }, [])

  const validate = useCallback((f) => {
    if (!f.type.startsWith('image/')) {
      return 'Only image files are accepted (PNG, JPG, GIF, WebP, etc.)'
    }
    if (f.size > MAX_SIZE) {
      return `File is too large (${formatSize(f.size)}). Maximum size is 5 MB.`
    }
    return null
  }, [])

  const processFile = useCallback((f) => {
    const err = validate(f)
    if (err) {
      setError(err)
      clearError()
      return
    }

    setError(null)
    setState('loading')

    const reader = new FileReader()
    reader.onload = (e) => {
      setPreview(e.target.result)
      setFile(f)
      setState('preview')
    }
    reader.onerror = () => {
      setError('Failed to read file. Please try again.')
      clearError()
      setState('idle')
    }
    reader.readAsDataURL(f)
  }, [validate, clearError])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) processFile(f)
  }, [processFile])

  const handleDragOver = useCallback((e) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleFileChange = useCallback((e) => {
    const f = e.target.files?.[0]
    if (f) processFile(f)
    e.target.value = ''
  }, [processFile])

  const handleDiscard = useCallback(() => {
    setPreview(null)
    setFile(null)
    setResult(null)
    setBasePrice('')
    setStockDate('')
    setState('idle')
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!preview || !file) return

    const price = parseFloat(basePrice)
    if (!basePrice || isNaN(price) || price <= 0) {
      setError('Please enter a valid base price.')
      clearError()
      return
    }
    if (!stockDate) {
      setError('Please enter the stock entry date.')
      clearError()
      return
    }

    setState('generating')
    try {
      const data = await submitImage(file, price, stockDate)
      saveImage(preview, file, data)
      setResult(data)
      setState('result')
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
      clearError()
      setState('preview')
    }
  }, [preview, file, basePrice, stockDate, clearError])

  const showPreviewCard = state === 'preview' || state === 'generating' || state === 'result'

  return (
    <div className="flex flex-col items-center">
      <div className="w-full max-w-xl">
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-text-primary mb-2">
          Upload Image
        </h1>
        <p className="text-text-secondary text-sm mb-8">
          Drag and drop an image or click to browse. Max 5 MB.
        </p>

        {/* Error message */}
        {error && (
          <div className="mb-4 flex items-center gap-3 rounded-xl bg-error-soft border border-error/20 px-4 py-3 text-sm text-error animate-fade-in">
            <Warning weight="bold" size={20} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Drop zone */}
        {state === 'idle' && (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => inputRef.current?.click()}
            className={[
              'group relative flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-12 sm:p-16 cursor-pointer transition-all duration-200',
              dragOver
                ? 'border-accent bg-accent-soft scale-[1.01]'
                : 'border-border hover:border-border-hover hover:bg-surface-raised',
            ].join(' ')}
          >
            <div
              className={[
                'flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-200',
                dragOver
                  ? 'bg-accent/20 text-accent'
                  : 'bg-surface-overlay text-text-muted group-hover:text-text-secondary group-hover:bg-surface-overlay',
              ].join(' ')}
            >
              <UploadSimple weight="duotone" size={32} />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-text-primary">
                {dragOver ? 'Drop your image here' : 'Drag & drop your image here'}
              </p>
              <p className="mt-1 text-xs text-text-muted">
                or click to browse &middot; PNG, JPG, GIF, WebP &middot; Max 5 MB
              </p>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>
        )}

        {state === 'loading' && (
          <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed border-accent/40 bg-accent-soft p-12 sm:p-16 animate-pulse-ring">
            <div className="h-10 w-10 rounded-full border-2 border-accent border-t-transparent animate-spin" />
            <p className="text-sm text-text-secondary">Processing image...</p>
          </div>
        )}

        {/* Preview card — stays visible during preview, generating, and result states */}
        {showPreviewCard && preview && (
          <div className="animate-fade-in">
            <div className="relative overflow-hidden rounded-2xl border border-border bg-surface-raised">
              {state === 'preview' && (
                <button
                  onClick={handleDiscard}
                  className="absolute top-3 right-3 z-10 flex h-9 w-9 items-center justify-center rounded-xl bg-surface/80 backdrop-blur-sm border border-border text-text-secondary hover:text-error hover:border-error/30 hover:bg-error-soft transition-all duration-200 cursor-pointer"
                  title="Remove image"
                >
                  <X weight="bold" size={16} />
                </button>
              )}
              <img
                src={preview}
                alt={file?.name || 'Preview'}
                className="w-full max-h-[400px] object-contain bg-surface-overlay"
              />
              {/* File info bar */}
              <div className="flex items-center justify-between gap-4 px-4 py-3 border-t border-border">
                <span className="text-sm text-text-secondary truncate">{file?.name}</span>
                <span className="text-xs text-text-muted shrink-0">{file && formatSize(file.size)}</span>
              </div>
            </div>

            {/* Form fields — only in preview state */}
            {state === 'preview' && (
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label htmlFor="basePrice" className="block text-xs font-medium text-text-secondary mb-1.5">
                    Base Price (Rp)
                  </label>
                  <input
                    id="basePrice"
                    type="number"
                    min="0"
                    step="1000"
                    placeholder="150000"
                    value={basePrice}
                    onChange={(e) => setBasePrice(e.target.value)}
                    className="w-full rounded-xl border border-border bg-surface-overlay px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all duration-200"
                  />
                </div>
                <div>
                  <label htmlFor="stockDate" className="block text-xs font-medium text-text-secondary mb-1.5">
                    Stock Entry Date
                  </label>
                  <input
                    id="stockDate"
                    type="date"
                    value={stockDate}
                    onChange={(e) => setStockDate(e.target.value)}
                    className="w-full rounded-xl border border-border bg-surface-overlay px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all duration-200 [color-scheme:dark]"
                  />
                </div>
              </div>
            )}

            {/* Submit button — only in preview state */}
            {state === 'preview' && (
              <button
                onClick={handleSubmit}
                className="mt-4 w-full flex items-center justify-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white transition-all duration-200 hover:bg-accent-hover active:scale-[0.98] cursor-pointer"
              >
                <CheckCircle weight="bold" size={18} />
                Submit
              </button>
            )}

            {/* Generating spinner */}
            {state === 'generating' && (
              <div className="mt-4 flex items-center justify-center gap-3 rounded-xl border border-border bg-surface-raised px-6 py-4 animate-fade-in">
                <SpinnerGap weight="bold" size={20} className="text-accent animate-spin" />
                <span className="text-sm font-medium text-text-secondary">Analyzing...</span>
              </div>
            )}

            {/* Result card */}
            {state === 'result' && result && (
              <div className="mt-4 space-y-3 animate-fade-in">
                {/* Archetype */}
                <div className="rounded-xl border border-border bg-surface-raised px-5 py-4">
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-1">Style Archetype</p>
                  <p className="text-lg font-semibold text-text-primary">
                    {result.archetype_classification?.label}
                  </p>
                </div>

                {/* Pricing */}
                <div className="rounded-xl border border-border bg-surface-raised px-5 py-4">
                  <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-2">Recommended Price</p>
                  <p className="text-2xl font-bold text-accent">
                    {formatCurrency(result.pricing?.recommended_price)}
                  </p>
                  <p className="text-sm text-text-secondary mt-1">
                    Expected value: {formatCurrency(result.pricing?.expected_value)}
                  </p>
                </div>

                {/* Trend */}
                {result.trend_phase && (
                  <div className="rounded-xl border border-border bg-surface-raised px-5 py-4">
                    <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-1">Trend Phase</p>
                    <p className="text-base font-semibold text-text-primary">
                      {result.trend_phase.current_state}
                    </p>
                  </div>
                )}

                {/* Advisor */}
                {result.advisor && (
                  <div className="rounded-xl border border-border bg-surface-raised px-5 py-4">
                    <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-2">AI Advisor</p>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {result.advisor.explanation}
                    </p>
                    {result.advisor.listing_caption_draft && (
                      <>
                        <p className="text-xs font-medium text-text-muted uppercase tracking-wide mt-4 mb-1">Listing Caption Draft</p>
                        <p className="text-sm text-text-primary leading-relaxed italic">
                          "{result.advisor.listing_caption_draft}"
                        </p>
                      </>
                    )}
                  </div>
                )}

                <button
                  onClick={handleDiscard}
                  className="w-full flex items-center justify-center gap-2 rounded-xl bg-surface-raised border border-border px-6 py-3 text-sm font-semibold text-text-secondary transition-all duration-200 hover:bg-surface-overlay hover:text-text-primary active:scale-[0.98] cursor-pointer"
                >
                  <ArrowCounterClockwise weight="bold" size={16} />
                  Upload another
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
