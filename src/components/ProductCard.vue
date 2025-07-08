<template>
    <el-card class="product-card" :body-style="{ padding: '0px' }" shadow="hover" @click.native="openProductLink">
        <div class="image-container">
            <el-image :src="product.image" fit="cover" class="product-image" :alt="product.name">
                <template #error>
                    <div class="image-error">
                        <el-icon>
                            <Picture />
                        </el-icon>
                        <span>图片加载失败</span>
                    </div>
                </template>
                <template #placeholder>
                    <div class="image-loading">
                        <el-icon>
                            <Loading />
                        </el-icon>
                    </div>
                </template>
            </el-image>
        </div>
        <div class="product-info">
            <div class="product-name" :title="product.name">{{ product.name }}</div>
            <div class="product-shop">
                <el-icon>
                    <Shop />
                </el-icon>
                <span>{{ product.shop }}</span>
            </div>
            <div class="product-price">
                <span class="current-price">¥{{ product.price }}</span>
                <span v-if="product.originalPrice" class="original-price">¥{{ product.originalPrice }}</span>
                <span v-if="product.sales" class="sales">月销{{ product.sales }}笔</span>
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
    window.open(props.product.link, '_blank')
}
</script>

<style scoped>
.product-card {
    width: 240px;
    margin: 10px;
    cursor: pointer;
    transition: all 0.3s;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.image-container {
    width: 100%;
    height: 240px;
    overflow: hidden;
}

.product-image {
    width: 100%;
    height: 100%;
    transition: transform 0.5s;
}

.product-card:hover .product-image {
    transform: scale(1.05);
}

.image-error,
.image-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #999;
    background-color: #f5f5f5;
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
}

.product-shop {
    margin-top: 8px;
    font-size: 12px;
    color: #999;
    display: flex;
    align-items: center;
}

.product-shop .el-icon {
    margin-right: 4px;
}

.product-price {
    margin-top: 8px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.current-price {
    color: #ff5000;
    font-size: 18px;
    font-weight: bold;
    margin-right: 8px;
}

.original-price {
    color: #999;
    font-size: 12px;
    text-decoration: line-through;
    margin-right: 8px;
}

.sales {
    color: #999;
    font-size: 12px;
}
</style>