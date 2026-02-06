<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
// 全局配置
useHead({
  htmlAttrs: {
    lang: 'zh-CN'
  }
})
</script>

<style>
/* 全局样式已通过 main.scss 引入 */
</style>
