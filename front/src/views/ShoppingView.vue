<template>
    <div class="chat-container">
        <!-- 商品卡片展示区 -->
        <div v-if="products.length > 0" class="product-display-area">
            <div class="product-grid">
                <div v-for="product in products" :key="product.id" class="product-card"
                    @click="openProductLink(product.link)">
                    <el-image :src="product.image" fit="cover" class="product-image" :alt="product.name">
                        <template #error>
                            <div class="image-error">
                                <el-icon>
                                    <Picture />
                                </el-icon>
                            </div>
                        </template>
                    </el-image>
                    <div class="product-info">
                        <div class="product-name">{{ product.name }}</div>
                        <div class="product-shop">
                            <el-icon>
                                <Shop />
                            </el-icon>
                            <span>{{ product.shop }}</span>
                        </div>
                        <div class="product-price">
                            <span class="current-price">¥{{ product.price }}</span>
                            <span v-if="product.originalPrice" class="original-price">¥{{ product.originalPrice
                            }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { Shop, Picture } from '@element-plus/icons-vue'

const inputMessage = ref('')
const isLoading = ref(false)
const messages = ref([])
const products = ref([])

const handleSubmit = async () => {
    if (!inputMessage.value.trim()) return

    isLoading.value = true
    messages.value.push({
        text: inputMessage.value,
        isUser: true
    })

    try {
        // 模拟API调用获取商品
        const response = await fetchProducts(inputMessage.value)
        products.value = response

        messages.value.push({
            text: `为您找到${response.length}件相关商品`,
            isUser: false
        })
    } catch (error) {
        console.error('获取商品失败:', error)
    } finally {
        isLoading.value = false
        inputMessage.value = ''
    }
}

const fetchProducts = async (keyword) => {
    // 替换为实际API调用
    return new Promise(resolve => {
        setTimeout(() => {
            resolve([
                {
                    id: '1',
                    name: `${keyword} 商品示例1`,
                    shop: '旗舰店',
                    price: '199.00',
                    originalPrice: '299.00',
                    image: 'https://via.placeholder.com/200',
                    link: 'https://example.com/product/1'
                },
                // 更多模拟商品...
            ])
        }, 800)
    })
}

const openProductLink = (url) => {
    window.open(url, '_blank')
}
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.chat-history {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.product-display-area {
    padding: 16px;
    border-top: 1px solid #eee;
}

.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 12px;
}

.product-card {
    border: 1px solid #eee;
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s;
}

.product-card:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}

.product-image {
    width: 100%;
    height: 160px;
    background-color: #f5f5f5;
}

.image-error {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    color: #999;
}

.product-info {
    padding: 12px;
}

.product-name {
    font-size: 14px;
    color: #333;
    margin-bottom: 8px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.product-shop {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: #999;
    margin-bottom: 8px;
}

.product-shop .el-icon {
    margin-right: 4px;
}

.product-price {
    display: flex;
    align-items: center;
}

.current-price {
    color: #f56c6c;
    font-size: 16px;
    font-weight: bold;
    margin-right: 8px;
}

.original-price {
    color: #999;
    font-size: 12px;
    text-decoration: line-through;
}

.chat-input-area {
    display: flex;
    padding: 16px;
    border-top: 1px solid #eee;
    background: #fff;
}

.chat-input-area .el-input {
    flex: 1;
    margin-right: 12px;
}
</style>