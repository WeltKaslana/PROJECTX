
import axios from "axios";  

// 按需导出
export const loadAll = () => {
    return axios.get('/back/student/')
}

export const load = (id) => {
    return axios.get(`/back/student/${id}`)
}