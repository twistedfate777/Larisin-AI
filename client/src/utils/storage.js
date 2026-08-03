const STORAGE_KEY = 'larisin_images'

export function getImages() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function saveImage(dataUrl, file, result) {
  const images = getImages()
  const entry = {
    id: crypto.randomUUID(),
    dataUrl,
    name: file.name,
    size: file.size,
    timestamp: Date.now(),
    result: result || null,
  }
  images.unshift(entry)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(images))
  return entry
}

export function removeImage(id) {
  const images = getImages().filter((img) => img.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(images))
  return images
}
