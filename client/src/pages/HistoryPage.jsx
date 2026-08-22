import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Trash, UploadSimple, ImageSquare } from '@phosphor-icons/react'
import { getImages, removeImage } from '../utils/storage'

function formatDate(ts) {
  return new Date(ts).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

export default function HistoryPage() {
  const [images, setImages] = useState([])

  useEffect(() => {
    setImages(getImages())
  }, [])

  const handleDelete = (id) => {
    const updated = removeImage(id)
    setImages(updated)
  }

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 animate-fade-in">
        <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-surface-raised border border-border mb-6">
          <ImageSquare weight="duotone" size={40} className="text-text-muted" />
        </div>
        <h2 className="text-xl font-semibold text-text-primary mb-2">No images yet</h2>
        <p className="text-sm text-text-secondary mb-6">
          Upload your first image to see it here.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-accent-hover active:scale-[0.98]"
        >
          <UploadSimple weight="bold" size={18} />
          Upload Image
        </Link>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-text-primary">
            History
          </h1>
          <p className="text-text-secondary text-sm mt-1">
            {images.length} image{images.length !== 1 ? 's' : ''} uploaded
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((img, i) => (
          <div
            key={img.id}
            className="group relative overflow-hidden rounded-2xl border border-border bg-surface-raised transition-all duration-200 hover:border-border-hover hover:shadow-lg hover:shadow-black/20"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="relative aspect-[4/3] bg-surface-overlay">
              <img
                src={img.dataUrl}
                alt={img.name}
                className="h-full w-full object-cover"
              />
              <button
                onClick={() => handleDelete(img.id)}
                className="absolute top-2.5 right-2.5 flex h-8 w-8 items-center justify-center rounded-lg bg-surface/80 backdrop-blur-sm border border-border text-text-secondary opacity-0 group-hover:opacity-100 hover:text-error hover:border-error/30 hover:bg-error-soft transition-all duration-200 cursor-pointer"
                title="Delete image"
              >
                <Trash weight="bold" size={14} />
              </button>
            </div>
            {img.result && (
              <div className="px-3.5 py-3 border-t border-border">
                {typeof img.result === 'object' ? (
                  <>
                    <p className="text-sm font-semibold text-text-primary">
                      {img.result.archetype_classification?.label}
                    </p>
                    <p className="mt-1 text-xs text-text-secondary">
                      Rp {Math.round(img.result.pricing?.recommended_price || 0).toLocaleString('id-ID')}
                    </p>
                  </>
                ) : (
                  <p className="text-sm text-text-secondary leading-relaxed">{img.result}</p>
                )}
              </div>
            )}
            <div className="px-3.5 py-3 border-t border-border">
              <p className="text-sm text-text-primary truncate">{img.name}</p>
              <div className="flex items-center justify-between mt-1">
                <span className="text-xs text-text-muted">{formatDate(img.timestamp)}</span>
                <span className="text-xs text-text-muted">{formatSize(img.size)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
