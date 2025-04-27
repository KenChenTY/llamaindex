import os
import logging
import time
import requests
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

import openai
import config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, 
                 api_key: Optional[str] = None, 
                 output_dir: Optional[str] = None,
                 model: str = "gpt-4o"):
        """
        初始化图像生成器
        
        Args:
            api_key: OpenAI API密钥
            output_dir: 图像输出目录
            model: 使用的模型名称
        """
        self.api_key = api_key or config.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY", "")
        
        if not self.api_key:
            raise ValueError("未提供OpenAI API密钥，请在.env文件中设置OPENAI_API_KEY或直接传入api_key参数")
        
        # 设置OpenAI客户端
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # 设置输出目录
        self.output_dir = output_dir or os.path.join(os.getcwd(), "generated_images")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.model = model
        logger.info(f"图像生成器初始化成功，输出目录: {self.output_dir}")
    
    def generate_image(self, 
                       prompt: str, 
                       size: str = "1024x1024", 
                       quality: str = "standard",
                       style: str = "vivid",
                       n: int = 1) -> List[Dict[str, Any]]:
        """
        生成图像
        
        Args:
            prompt: 图像描述提示
            size: 图像尺寸，可选值为 "1024x1024", "1792x1024", "1024x1792"
            quality: 图像质量，可选值为 "standard", "hd"
            style: 图像风格，可选值为 "vivid", "natural"
            n: 生成图像数量
            
        Returns:
            包含图像URL和保存路径的字典列表
        """
        logger.info(f"生成图像，提示: {prompt}")
        
        try:
            # 调用DALL-E 3 API生成图像
            response = self.client.images.generate(
                model="dall-e-3",  # 目前GPT-4o需要通过dall-e-3来生成图像
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
                n=n
            )
            
            result = []
            
            # 处理生成的图像
            for i, image_data in enumerate(response.data):
                image_url = image_data.url
                
                # 下载图像
                image_response = requests.get(image_url)
                image = Image.open(BytesIO(image_response.content))
                
                # 生成文件名并保存
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"image_{timestamp}_{i}.png"
                save_path = os.path.join(self.output_dir, filename)
                
                image.save(save_path)
                logger.info(f"图像已保存到: {save_path}")
                
                result.append({
                    "url": image_url,
                    "local_path": save_path,
                    "prompt": prompt
                })
            
            return result
            
        except Exception as e:
            logger.error(f"生成图像时出错: {str(e)}")
            return []
    
    def generate_image_with_text_analysis(self, text: str) -> List[Dict[str, Any]]:
        """
        通过文本分析生成图像
        
        首先使用GPT-4o分析文本以创建更好的图像描述提示，然后生成图像
        
        Args:
            text: 用户输入的文本描述
            
        Returns:
            包含图像URL和保存路径的字典列表
        """
        logger.info(f"分析文本并生成图像: {text}")
        
        try:
            # 使用GPT-4o分析文本并创建更好的图像提示
            prompt_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的图像描述专家。你的任务是将用户的文本转换为详细、生动的图像生成提示。描述应该具体、富有想象力，并包含关键视觉细节，如光线、颜色、构图和风格。提示应该是中文的，长度适中（100-150字左右），并且能够捕捉用户意图的精髓。只返回图像描述，不要有其他解释或前缀。"},
                    {"role": "user", "content": f"请为以下文本创建一个图像生成提示：\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            # 提取优化后的提示
            enhanced_prompt = prompt_response.choices[0].message.content.strip()
            logger.info(f"优化后的图像提示: {enhanced_prompt}")
            
            # 使用优化后的提示生成图像
            return self.generate_image(enhanced_prompt)
            
        except Exception as e:
            logger.error(f"文本分析生成图像时出错: {str(e)}")
            return [] 