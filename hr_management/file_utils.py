"""
文件处理工具

提供文件上传、验证、处理等功能
"""
import os
import uuid
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.exceptions import ValidationError


# ============ 文件配置 ============

FILE_CONFIG = {
    # 图片配置
    'image': {
        'max_size': 5 * 1024 * 1024,  # 5MB
        'allowed_extensions': {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'},
        'allowed_mimetypes': {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'},
    },
    # 文档配置
    'document': {
        'max_size': 20 * 1024 * 1024,  # 20MB
        'allowed_extensions': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'},
        'allowed_mimetypes': {
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
        },
    },
    # 压缩包配置
    'archive': {
        'max_size': 50 * 1024 * 1024,  # 50MB
        'allowed_extensions': {'zip', 'rar', '7z'},
        'allowed_mimetypes': {
            'application/zip',
            'application/x-rar-compressed',
            'application/x-7z-compressed',
        },
    },
    # 发票配置
    'invoice': {
        'max_size': 10 * 1024 * 1024,  # 10MB
        'allowed_extensions': {'jpg', 'jpeg', 'png', 'pdf'},
        'allowed_mimetypes': {'image/jpeg', 'image/png', 'application/pdf'},
    },
}


class FileValidator:
    """文件验证器"""

    def __init__(self, file_type='image', custom_config=None):
        self.config = custom_config or FILE_CONFIG.get(file_type, FILE_CONFIG['image'])

    def validate(self, file):
        """验证文件"""
        errors = []

        # 验证文件大小
        if file.size > self.config['max_size']:
            max_mb = self.config['max_size'] / (1024 * 1024)
            errors.append(f'文件大小不能超过 {max_mb:.1f}MB')

        # 验证扩展名
        ext = self._get_extension(file.name)
        if ext not in self.config['allowed_extensions']:
            allowed = ', '.join(self.config['allowed_extensions'])
            errors.append(f'不支持的文件类型，允许: {allowed}')

        # 验证 MIME 类型
        mimetype = self._get_mimetype(file)
        if mimetype and mimetype not in self.config['allowed_mimetypes']:
            errors.append('文件类型与扩展名不匹配')

        if errors:
            raise ValidationError(errors)

        return True

    def _get_extension(self, filename):
        """获取文件扩展名"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    def _get_mimetype(self, file):
        """获取文件 MIME 类型"""
        # 尝试从文件对象获取
        if hasattr(file, 'content_type'):
            return file.content_type

        # 从文件名推断
        mimetype, _ = mimetypes.guess_type(file.name)
        return mimetype


class FileProcessor:
    """文件处理器"""

    @staticmethod
    def generate_filename(original_name, prefix=''):
        """生成唯一文件名"""
        ext = original_name.rsplit('.', 1)[-1].lower() if '.' in original_name else ''
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:8]

        if prefix:
            return f'{prefix}_{timestamp}_{unique_id}.{ext}'
        return f'{timestamp}_{unique_id}.{ext}'

    @staticmethod
    def get_file_hash(file):
        """计算文件哈希值（用于去重）"""
        hasher = hashlib.md5()

        # 保存当前位置
        pos = file.tell()
        file.seek(0)

        for chunk in file.chunks():
            hasher.update(chunk)

        # 恢复位置
        file.seek(pos)

        return hasher.hexdigest()

    @staticmethod
    def organize_path(base_path, file_type='default'):
        """
        组织文件存储路径

        按日期分目录：base_path/file_type/YYYY/MM/
        """
        now = datetime.now()
        return os.path.join(
            base_path,
            file_type,
            str(now.year),
            f'{now.month:02d}'
        )


class ImageProcessor:
    """图片处理器"""

    # 默认缩略图尺寸
    THUMBNAIL_SIZES = {
        'small': (100, 100),
        'medium': (300, 300),
        'large': (800, 800),
    }

    # 最大图片尺寸（超过将压缩）
    MAX_DIMENSION = 2048

    # JPEG 质量
    JPEG_QUALITY = 85

    # 头像配置
    AVATAR_SIZE = (200, 200)  # 头像尺寸
    AVATAR_QUALITY = 80       # 头像质量

    @classmethod
    def process_avatar(cls, file):
        """
        处理头像图片

        - 压缩到 200x200
        - 质量 80%
        - 转为 JPEG
        - 预计大小: 10-30KB
        """
        try:
            img = Image.open(file)

            # 转换 RGBA 到 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 裁剪为正方形（居中裁剪）
            width, height = img.size
            if width != height:
                size = min(width, height)
                left = (width - size) // 2
                top = (height - size) // 2
                img = img.crop((left, top, left + size, top + size))

            # 缩放到目标尺寸
            img = img.resize(cls.AVATAR_SIZE, Image.Resampling.LANCZOS)

            # 保存到内存
            output = BytesIO()
            img.save(output, format='JPEG', quality=cls.AVATAR_QUALITY, optimize=True)
            output.seek(0)

            # 生成新文件名
            original_name = getattr(file, 'name', 'avatar.jpg')
            new_name = original_name.rsplit('.', 1)[0] + '.jpg'

            return InMemoryUploadedFile(
                file=output,
                field_name=None,
                name=new_name,
                content_type='image/jpeg',
                size=output.getbuffer().nbytes,
                charset=None
            )
        except Exception as e:
            # 如果处理失败，返回原文件
            if hasattr(file, 'seek'):
                file.seek(0)
            return file

    @classmethod
    def process_image(cls, file, max_dimension=None, quality=None):
        """
        处理上传的图片

        - 压缩大图
        - 转换为 JPEG（可选）
        - 返回处理后的文件
        """
        max_dimension = max_dimension or cls.MAX_DIMENSION
        quality = quality or cls.JPEG_QUALITY

        try:
            img = Image.open(file)

            # 转换 RGBA 到 RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background

            # 检查是否需要压缩
            width, height = img.size
            if width > max_dimension or height > max_dimension:
                # 等比缩放
                ratio = min(max_dimension / width, max_dimension / height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 保存到内存
            output = BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            output.seek(0)

            # 生成新文件名
            original_name = file.name
            new_name = original_name.rsplit('.', 1)[0] + '.jpg'

            return InMemoryUploadedFile(
                file=output,
                field_name=None,
                name=new_name,
                content_type='image/jpeg',
                size=output.getbuffer().nbytes,
                charset=None
            )
        except Exception as e:
            # 如果处理失败，返回原文件
            file.seek(0)
            return file

    @classmethod
    def create_thumbnail(cls, file, size='medium'):
        """创建缩略图"""
        dimensions = cls.THUMBNAIL_SIZES.get(size, cls.THUMBNAIL_SIZES['medium'])

        try:
            img = Image.open(file)

            # 转换模式
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # 创建缩略图（保持比例）
            img.thumbnail(dimensions, Image.Resampling.LANCZOS)

            output = BytesIO()
            img.save(output, format='JPEG', quality=80, optimize=True)
            output.seek(0)

            return output
        except Exception:
            return None

    @classmethod
    def get_image_info(cls, file):
        """获取图片信息"""
        try:
            img = Image.open(file)
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
            }
        except Exception:
            return None


def upload_to_path(instance, filename, base_path='uploads'):
    """
    Django FileField 的 upload_to 函数

    Example:
        avatar = models.ImageField(upload_to=lambda i, f: upload_to_path(i, f, 'avatars'))
    """
    processor = FileProcessor()
    organized_path = processor.organize_path(base_path)
    new_filename = processor.generate_filename(filename)
    return os.path.join(organized_path, new_filename)


def validate_and_process_image(file, max_size_mb=5, max_dimension=2048):
    """
    验证并处理上传的图片

    Returns:
        处理后的文件对象

    Raises:
        ValidationError: 验证失败
    """
    # 验证
    validator = FileValidator('image', {
        'max_size': max_size_mb * 1024 * 1024,
        'allowed_extensions': FILE_CONFIG['image']['allowed_extensions'],
        'allowed_mimetypes': FILE_CONFIG['image']['allowed_mimetypes'],
    })
    validator.validate(file)

    # 处理
    return ImageProcessor.process_image(file, max_dimension=max_dimension)


def validate_document(file, max_size_mb=20):
    """
    验证上传的文档

    Raises:
        ValidationError: 验证失败
    """
    validator = FileValidator('document', {
        'max_size': max_size_mb * 1024 * 1024,
        'allowed_extensions': FILE_CONFIG['document']['allowed_extensions'],
        'allowed_mimetypes': FILE_CONFIG['document']['allowed_mimetypes'],
    })
    validator.validate(file)
    return file
