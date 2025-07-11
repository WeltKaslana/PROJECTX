<template>
  <el-card 
    class="product-card" 
    :body-style="{ padding: '0px' }" 
    shadow="hover"
    @click.stop="openProductLink"
  >
    <div class="image-container">
      <el-image 
        :src="product.image" 
        fit="cover" 
        class="product-image" 
        :alt="product.name"
        lazy
        :preview-src-list="[product.image]"
        hide-on-click-modal
      >
        <template #error>
          <div class="image-error">
            <el-icon><Picture /></el-icon>
            <span>图片加载失败</span>
          </div>
        </template>
        <template #placeholder>
          <div class="image-loading">
            <el-icon><Loading /></el-icon>
          </div>
        </template>
      </el-image>
      <div class="product-badge" v-if="product.isPostFree">
        包邮
      </div>
    </div>
    <div class="product-info">
      <div class="product-name" :title="product.name">
        {{ product.name }}
      </div>
      
      <div class="product-meta">
        <div class="product-shop" @click.stop="openShopLink">
          <el-icon><Shop /></el-icon>
          <span class="shop-name">{{ product.shop }}</span>
          <span class="location" v-if="product.location">
            {{ product.location }}
          </span>
        </div>
        
        <div class="product-price">
          <span class="current-price">¥{{ product.price }}</span>
          <span class="sales">销量 {{ formatSalesDisplay(product.sales) }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { Shop, Picture, Loading } from '@element-plus/icons-vue'

const props = defineProps({
  product: {
    type: Object,
    required: true,
    validator: (value) => {
      return value.id && value.name && value.price
    }
  }
})

const openProductLink = () => {
  if (props.product.link && props.product.link !== '#') {
    window.open(props.product.link.startsWith('http') ? 
      props.product.link : 
      `https://${props.product.link}`, '_blank')
  }
}

const openShopLink = (e) => {
  e.stopPropagation()
  if (props.product.shopLink && props.product.shopLink !== '#') {
    window.open(props.product.shopLink.startsWith('http') ? 
      props.product.shopLink : 
      `https://${props.product.shopLink}`, '_blank')
  }
}

const formatSalesDisplay = (sales) => {
  if (sales >= 10000) {
    return `${(sales / 10000).toFixed(1)}万+`
  }
  return sales || 0
}
</script>

<style scoped>
/* 原有样式保持不变 */
.product-card {
  width: 100%;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.image-container {
  width: 100%;
  height: 0;
  padding-bottom: 100%;
  position: relative;
  overflow: hidden;
  background: #f5f7fa;
}

.product-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.product-card:hover .product-image {
  transform: scale(1.03);
}

.image-error,
.image-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
  background: #f5f5f5;
}

.product-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--el-color-success);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 1;
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  height: 42px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.product-shop {
  display: flex;
  align-items: center;
  font-size: 12px;
  color: #666;
  transition: color 0.2s;
}

.product-shop:hover {
  color: var(--el-color-primary);
}

.shop-name {
  margin: 0 4px;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.location {
  color: #999;
  font-size: 11px;
}

.product-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.current-price {
  color: #ff5000;
  font-size: 16px;
  font-weight: bold;
}

.sales {
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .product-name {
    font-size: 13px;
    height: 36px;
  }
  
  .current-price {
    font-size: 15px;
  }
}
</style>