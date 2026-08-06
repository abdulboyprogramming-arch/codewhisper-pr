/// <reference types="next" />
/// <reference types="next/types/global" />
/// <reference types="next/image-types/global" />

type ThemeCustomFonts = {
  fonts: {
    sans: 'Inter, system-ui, sans-serif',
  }
}

declare const ThemeCustomFonts: ThemeCustomFonts

type NextImageConfig = {
  remotePatterns: Array<{
    protocol?: 'http' | 'https'
    hostname: string
    port?: string
    pathname?: string
  }>
}

declare const imageConfig: NextImageConfig

export {}
