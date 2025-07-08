<template>
  <div class="product-list-container">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>
    
    <div v-else-if="products.length === 0" class="empty-container">
      <el-empty description="暂无商品数据" />
    </div>
    
    <div v-else class="product-list">
      <ProductCard 
        v-for="product in products" 
        :key="product.id" 
        :product="product"
      />
    </div>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="prev, pager, next, jumper"
        @current-change="fetchProducts"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProductCard from './ProductCard.vue'

const products = ref([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

// 模拟API获取商品数据
const fetchProducts = async () => {
  try {
    loading.value = true
    // 这里替换为实际的API调用
    const response = await mockApiFetchProducts({
      page: currentPage.value,
      size: pageSize.value
    })
    
    products.value = response.data
    total.value = response.total
  } catch (error) {
    console.error('获取商品失败:', error)
  } finally {
    loading.value = false
  }
}

// 模拟API
const mockApiFetchProducts = ({ page, size }) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockData = Array.from({ length: size }, (_, i) => ({
        id: `prod_${page}_${i}`,
        name: `商品名称 ${i + 1} 这是商品详细描述信息`,
        shop: `店铺名称 ${i + 1}`,
        price: (Math.random() * 1000).toFixed(2),
        originalPrice: (Math.random() * 1200).toFixed(2),
        sales: Math.floor(Math.random() * 10000),
        image: `https://picsum.photos/300/300?random=${page}_${i}`,
        link: `https://example.com/product/${page}_${i}`
      }))
      
      resolve({
        data: mockData,
        total: 100
      })
    }, 500)
  })
}

onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.product-list-container {
  padding: 20px;
}

.loading-container {
  padding: 20px;
}

.product-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.empty-container {
  padding: 40px 0;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>