# Vue 前端 Dockerfile
FROM node:18-alpine as build

WORKDIR /app

# 配置淘宝镜像加速
RUN npm config set registry https://registry.npmmirror.com

# 复制 package.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源码
COPY . .

# 设置环境变量并构建
ENV VITE_API_BASE_URL=/api
# 高德地图配置从构建参数获取（服务器上通过 --build-arg 传入）
ARG VITE_AMAP_KEY=""
ARG VITE_AMAP_SECURITY_JS_CODE=""
ENV VITE_AMAP_KEY=${VITE_AMAP_KEY}
ENV VITE_AMAP_SECURITY_JS_CODE=${VITE_AMAP_SECURITY_JS_CODE}
RUN npm run build

# 生产环境 - nginx
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
