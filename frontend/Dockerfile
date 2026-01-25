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
ENV VITE_AMAP_KEY=a854e5d1b219fe66f65d64dd26b0f0b2
ENV VITE_AMAP_SECURITY_JS_CODE=861d33a480c4e5e935f1afd2506f86eb
RUN npm run build

# 生产环境 - nginx
FROM nginx:alpine

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
