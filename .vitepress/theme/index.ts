import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import Flashcards from './components/Flashcards.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('Flashcards', Flashcards)
  },
} satisfies Theme
