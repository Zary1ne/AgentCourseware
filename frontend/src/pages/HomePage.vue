<template>
  <div class="homepage">
    <Navbar />
    <Hero />
    <ProductPreview />
    <div class="section-divider" />
    <ProcessFlow />
    <div class="section-divider" />
    <ProjectStats />
    <div class="section-divider" />
    <FeatureEngine />
    <div class="section-divider" />
    <FeaturedProjects />
    <BottomCTA />
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '../components/Navbar.vue'
import Hero from '../components/Hero.vue'
import ProductPreview from '../components/ProductPreview.vue'
import ProcessFlow from '../components/ProcessFlow.vue'
import ProjectStats from '../components/ProjectStats.vue'
import FeatureEngine from '../components/FeatureEngine.vue'
import FeaturedProjects from '../components/FeaturedProjects.vue'
import BottomCTA from '../components/BottomCTA.vue'
import Footer from '../components/Footer.vue'
</script>
