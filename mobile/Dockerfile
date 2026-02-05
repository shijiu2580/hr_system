# 构建阶段
FROM node:22-alpine as builder

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源码
COPY . .

# 设置环境变量（构建时）
ARG VITE_API_BASE_URL=/api
ARG VITE_AMAP_KEY=c66f75e5da10fa69ee4c5e6a8d2997e7
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_AMAP_KEY=$VITE_AMAP_KEY

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
