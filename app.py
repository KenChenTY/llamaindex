import os
import logging
import argparse
from typing import Optional, List, Dict, Any

from document_processor import DocumentProcessor
from query_engine import QueryEngine, DEFAULT_QUERY_TEMPLATE
from image_generator import ImageGenerator
from llama_index.core.prompts import PromptTemplate
import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argparse():
    """设置命令行参数"""
    parser = argparse.ArgumentParser(description='LlamaIndex RAG 应用')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 索引命令
    index_parser = subparsers.add_parser('index', help='索引文档')
    index_parser.add_argument(
        '--docs_dir', 
        type=str, 
        default=config.DOCUMENTS_DIR,
        help='文档目录路径'
    )
    
    # 查询命令
    query_parser = subparsers.add_parser('query', help='查询知识库')
    query_parser.add_argument(
        '--query', 
        type=str, 
        help='查询文本'
    )
    query_parser.add_argument(
        '--system_prompt', 
        type=str, 
        default=config.SYSTEM_PROMPT,
        help='系统提示'
    )
    
    # 更新提示词命令
    prompt_parser = subparsers.add_parser('update_prompt', help='更新提示词')
    prompt_parser.add_argument(
        '--system_prompt', 
        type=str, 
        required=True,
        help='新的系统提示'
    )
    
    # 图像生成命令
    image_parser = subparsers.add_parser('generate_image', help='生成图像')
    image_parser.add_argument(
        '--prompt', 
        type=str, 
        required=True,
        help='图像描述提示'
    )
    image_parser.add_argument(
        '--size', 
        type=str, 
        default=config.IMAGE_SIZE,
        help='图像尺寸 (1024x1024, 1792x1024, 1024x1792)'
    )
    image_parser.add_argument(
        '--quality', 
        type=str, 
        default=config.IMAGE_QUALITY,
        help='图像质量 (standard, hd)'
    )
    image_parser.add_argument(
        '--style', 
        type=str, 
        default=config.IMAGE_STYLE,
        help='图像风格 (vivid, natural)'
    )
    image_parser.add_argument(
        '--analyze', 
        action='store_true',
        help='使用GPT-4o分析文本以创建更好的图像描述'
    )
    
    # 交互式命令
    interactive_parser = subparsers.add_parser('interactive', help='交互式模式')
    
    return parser

def index_documents(docs_dir: str = config.DOCUMENTS_DIR) -> None:
    """
    索引文档
    
    Args:
        docs_dir: 文档目录路径
    """
    logger.info(f"开始索引文档，目录: {docs_dir}")
    
    processor = DocumentProcessor(documents_dir=docs_dir)
    documents = processor.load_documents()
    
    if not documents:
        logger.warning(f"目录 {docs_dir} 中没有找到文档")
        print(f"错误: 目录 {docs_dir} 中没有找到文档")
        return
    
    logger.info(f"找到 {len(documents)} 个文档，开始处理...")
    index = processor.process_documents(documents)
    
    if index:
        logger.info("文档索引创建成功")
        print(f"成功: {len(documents)} 个文档已成功索引")
    else:
        logger.error("文档索引创建失败")
        print("错误: 文档索引创建失败")

def process_query(query_text: str, system_prompt: Optional[str] = None) -> str:
    """
    处理查询
    
    Args:
        query_text: 查询文本
        system_prompt: 系统提示
        
    Returns:
        查询结果
    """
    engine = QueryEngine()
    
    if system_prompt and system_prompt != config.SYSTEM_PROMPT:
        engine.update_prompt(system_prompt=system_prompt)
    
    return engine.query(query_text)

def update_system_prompt(new_prompt: str) -> None:
    """
    更新系统提示
    
    Args:
        new_prompt: 新的系统提示
    """
    # 将新提示保存到环境变量文件
    with open(".env", "a") as f:
        f.write(f'\nSYSTEM_PROMPT="{new_prompt}"\n')
    
    print(f"系统提示已更新并保存到.env文件")

def generate_image(prompt: str, 
                  size: str = config.IMAGE_SIZE, 
                  quality: str = config.IMAGE_QUALITY, 
                  style: str = config.IMAGE_STYLE,
                  analyze: bool = False) -> List[Dict[str, Any]]:
    """
    生成图像
    
    Args:
        prompt: 图像描述提示
        size: 图像尺寸
        quality: 图像质量
        style: 图像风格
        analyze: 是否使用GPT-4o分析文本
        
    Returns:
        生成的图像信息列表
    """
    generator = ImageGenerator(
        output_dir=config.IMAGE_OUTPUT_DIR,
        model=config.IMAGE_MODEL
    )
    
    try:
        if analyze:
            print("正在使用GPT-4o分析文本以创建更好的图像描述...")
            images = generator.generate_image_with_text_analysis(prompt)
        else:
            images = generator.generate_image(
                prompt=prompt,
                size=size,
                quality=quality,
                style=style
            )
            
        if images:
            print(f"成功生成 {len(images)} 张图像:")
            for img in images:
                print(f"- 保存路径: {img['local_path']}")
            return images
        else:
            print("图像生成失败")
            return []
            
    except Exception as e:
        print(f"图像生成出错: {str(e)}")
        return []

def interactive_mode():
    """交互式查询模式"""
    engine = QueryEngine()
    generator = ImageGenerator(
        output_dir=config.IMAGE_OUTPUT_DIR,
        model=config.IMAGE_MODEL
    )
    
    print("\n=== LlamaIndex RAG 交互式模式 ===")
    print("输入 'exit' 或 'quit' 退出")
    print("输入 'prompt' 更新系统提示")
    print("输入 'reload' 重新加载索引")
    print("输入 'image:描述' 生成图像")
    print("输入 'analyze_image:描述' 使用GPT-4o分析并生成图像")
    print("===================================\n")
    
    while True:
        user_input = input("\n请输入您的问题 > ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("再见!")
            break
        
        elif user_input.lower() == 'prompt':
            new_prompt = input("请输入新的系统提示 > ")
            engine.update_prompt(system_prompt=new_prompt)
            print("系统提示已更新")
            continue
            
        elif user_input.lower() == 'reload':
            engine = QueryEngine()
            print("索引已重新加载")
            continue
            
        elif user_input.lower().startswith('image:'):
            image_prompt = user_input[6:].strip()
            if not image_prompt:
                print("请提供图像描述")
                continue
                
            print(f"正在生成图像: {image_prompt}")
            generate_image(image_prompt)
            continue
            
        elif user_input.lower().startswith('analyze_image:'):
            image_prompt = user_input[14:].strip()
            if not image_prompt:
                print("请提供图像描述")
                continue
                
            print(f"正在分析并生成图像: {image_prompt}")
            generate_image(image_prompt, analyze=True)
            continue
        
        # 处理普通查询
        response = engine.query(user_input)
        print("\n回答:")
        print(response)

def main():
    """主函数"""
    parser = setup_argparse()
    args = parser.parse_args()
    
    # 确保OpenAI API密钥已设置
    if not config.OPENAI_API_KEY:
        print("警告: 未设置OPENAI_API_KEY环境变量")
        api_key = input("请输入您的OpenAI API密钥 > ")
        os.environ["OPENAI_API_KEY"] = api_key
        
        # 保存到.env文件
        with open(".env", "a") as f:
            f.write(f'\nOPENAI_API_KEY="{api_key}"\n')
    
    # 处理命令
    if args.command == 'index':
        index_documents(args.docs_dir)
    
    elif args.command == 'query':
        if args.query:
            result = process_query(args.query, args.system_prompt)
            print("\n回答:")
            print(result)
        else:
            print("错误: 请提供查询文本")
    
    elif args.command == 'update_prompt':
        update_system_prompt(args.system_prompt)
        
    elif args.command == 'generate_image':
        generate_image(
            prompt=args.prompt,
            size=args.size,
            quality=args.quality,
            style=args.style,
            analyze=args.analyze
        )
    
    elif args.command == 'interactive' or not args.command:
        # 默认使用交互式模式
        interactive_mode()
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 