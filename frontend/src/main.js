import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './index.css'

const app = createApp(App)
app.use(createPinia())

// Global directive: v-scroll-in — adds .in-view when element enters viewport
app.directive('scroll-in', {
  mounted(el, binding) {
    el.classList.add('scroll-in')
    if (binding.value && binding.value.delay) {
      el.style.transitionDelay = binding.value.delay + 'ms'
    }
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view')
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: binding.value?.threshold ?? 0.15 })
    observer.observe(el)
    el._scrollObserver = observer
  },
  unmounted(el) {
    if (el._scrollObserver) el._scrollObserver.disconnect()
  }
})

app.use(router).mount('#app')