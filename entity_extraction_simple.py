#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产业知识图谱 - 实体识别与抽取Demo (简化版)
作者：算法工程师
功能：从专利文本中抽取企业、产品、技术等实体及其关系
"""

import json
import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import jieba
import jieba.posseg as pseg
import warnings
warnings.filterwarnings('ignore')

class IndustryEntityExtractor:
    """产业实体抽取器"""
    
    def __init__(self):
        self.enterprise_dict = set()
        self.product_dict = set()
        self.technology_dict = set()
        self.industry_dict = set()
        self.location_dict = set()
        
        # 初始化词典
        self._init_dictionaries()
        
        # 实体类型映射
        self.entity_types = {
            'enterprise': '企业',
            'product': '产品', 
            'technology': '技术',
            'industry': '产业',
            'location': '地理'
        }
        
        # 关系类型定义
        self.relation_types = {
            'supply': '供应关系',
            'technology': '技术关系',
            'compete': '竞争关系',
            'cooperate': '合作关系'
        }
    
    def _init_dictionaries(self):
        """初始化各类实体词典"""
        
        # 企业词典（模拟数据）
        self.enterprise_dict = {
            '华为技术有限公司', '华为', 'HUAWEI',
            '中兴通讯股份有限公司', '中兴', 'ZTE',
            '小米科技有限公司', '小米', 'Xiaomi',
            'OPPO广东移动通信有限公司', 'OPPO',
            'vivo移动通信有限公司', 'vivo',
            '比亚迪股份有限公司', '比亚迪', 'BYD',
            '宁德时代新能源科技股份有限公司', '宁德时代', 'CATL',
            '京东方科技集团股份有限公司', '京东方', 'BOE',
            '海康威视数字技术股份有限公司', '海康威视', 'Hikvision',
            '大疆创新科技有限公司', '大疆', 'DJI'
        }
        
        # 产品词典
        self.product_dict = {
            '智能手机', '手机', '平板电脑', '笔记本电脑', '智能手表',
            '新能源汽车', '电动汽车', '混合动力汽车', '动力电池',
            '液晶显示屏', 'OLED屏幕', '柔性屏', '摄像头', '传感器',
            '无人机', '机器人', '芯片', '处理器', '存储器'
        }
        
        # 技术词典
        self.technology_dict = {
            '5G技术', '人工智能', '机器学习', '深度学习', '计算机视觉',
            '自然语言处理', '语音识别', '图像识别', '自动驾驶',
            '物联网', '云计算', '大数据', '区块链', '量子计算',
            '新能源技术', '电池技术', '充电技术', '半导体技术'
        }
        
        # 产业词典
        self.industry_dict = {
            '电子信息产业', '通信设备制造业', '计算机设备制造业',
            '新能源汽车产业', '动力电池产业', '半导体产业',
            '人工智能产业', '物联网产业', '智能制造产业',
            '生物医药产业', '新材料产业', '节能环保产业'
        }
        
        # 地理词典
        self.location_dict = {
            '深圳', '北京', '上海', '广州', '杭州', '成都', '武汉',
            '西安', '南京', '苏州', '无锡', '东莞', '佛山', '珠海',
            '广东省', '江苏省', '浙江省', '山东省', '四川省'
        }
    
    def extract_entities(self, text: str) -> List[Dict]:
        """从文本中抽取实体"""
        entities = []
        
        # 1. 基于词典的精确匹配
        entities.extend(self._dict_based_extraction(text))
        
        # 2. 基于规则的抽取
        entities.extend(self._rule_based_extraction(text))
        
        # 3. 基于词性标注的抽取
        entities.extend(self._pos_based_extraction(text))
        
        # 去重和排序
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _dict_based_extraction(self, text: str) -> List[Dict]:
        """基于词典的实体抽取"""
        entities = []
        
        # 企业实体抽取
        for enterprise in self.enterprise_dict:
            if enterprise in text:
                entities.append({
                    'text': enterprise,
                    'type': 'enterprise',
                    'start': text.find(enterprise),
                    'end': text.find(enterprise) + len(enterprise),
                    'confidence': 0.95
                })
        
        # 产品实体抽取
        for product in self.product_dict:
            if product in text:
                entities.append({
                    'text': product,
                    'type': 'product',
                    'start': text.find(product),
                    'end': text.find(product) + len(product),
                    'confidence': 0.9
                })
        
        # 技术实体抽取
        for technology in self.technology_dict:
            if technology in text:
                entities.append({
                    'text': technology,
                    'type': 'technology',
                    'start': text.find(technology),
                    'end': text.find(technology) + len(technology),
                    'confidence': 0.9
                })
        
        # 产业实体抽取
        for industry in self.industry_dict:
            if industry in text:
                entities.append({
                    'text': industry,
                    'type': 'industry',
                    'start': text.find(industry),
                    'end': text.find(industry) + len(industry),
                    'confidence': 0.85
                })
        
        # 地理实体抽取
        for location in self.location_dict:
            if location in text:
                entities.append({
                    'text': location,
                    'type': 'location',
                    'start': text.find(location),
                    'end': text.find(location) + len(location),
                    'confidence': 0.9
                })
        
        return entities
    
    def _rule_based_extraction(self, text: str) -> List[Dict]:
        """基于规则的实体抽取"""
        entities = []
        
        # 企业名称模式：XX有限公司、XX股份有限公司、XX科技公司等
        enterprise_patterns = [
            r'([\u4e00-\u9fa5]+(?:技术|科技|通信|电子|新能源|智能|数字|创新|集团|股份|有限|责任)公司)',
            r'([A-Z]+)',
        ]
        
        for pattern in enterprise_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_text = match.group(1)
                if len(entity_text) >= 3:  # 过滤太短的匹配
                    entities.append({
                        'text': entity_text,
                        'type': 'enterprise',
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.7
                    })
        
        # 产品型号模式：XX-XXX、XX XXX等
        product_patterns = [
            r'([A-Za-z]+[- ]?\d+[A-Za-z]*)',
        ]
        
        for pattern in product_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                entity_text = match.group(1)
                if len(entity_text) >= 3:
                    entities.append({
                        'text': entity_text,
                        'type': 'product',
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.6
                    })
        
        return entities
    
    def _pos_based_extraction(self, text: str) -> List[Dict]:
        """基于词性标注的实体抽取"""
        entities = []
        
        # 使用jieba进行词性标注
        words = pseg.cut(text)
        
        for word, flag in words:
            # 组织机构名词
            if flag == 'nt' and len(word) >= 2:
                entities.append({
                    'text': word,
                    'type': 'enterprise',
                    'start': text.find(word),
                    'end': text.find(word) + len(word),
                    'confidence': 0.6
                })
            
            # 地名
            elif flag == 'ns' and len(word) >= 2:
                entities.append({
                    'text': word,
                    'type': 'location',
                    'start': text.find(word),
                    'end': text.find(word) + len(word),
                    'confidence': 0.7
                })
            
            # 名词
            elif flag == 'n' and len(word) >= 2:
                # 简单的启发式规则判断实体类型
                if any(keyword in word for keyword in ['技术', '算法', '系统', '平台']):
                    entities.append({
                        'text': word,
                        'type': 'technology',
                        'start': text.find(word),
                        'end': text.find(word) + len(word),
                        'confidence': 0.5
                    })
                elif any(keyword in word for keyword in ['产业', '行业', '领域']):
                    entities.append({
                        'text': word,
                        'type': 'industry',
                        'start': text.find(word),
                        'end': text.find(word) + len(word),
                        'confidence': 0.5
                    })
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """实体去重和排序"""
        # 按位置排序
        entities.sort(key=lambda x: x['start'])
        
        # 去重（保留置信度最高的）
        unique_entities = []
        seen_positions = set()
        
        for entity in entities:
            position_key = (entity['start'], entity['end'])
            if position_key not in seen_positions:
                seen_positions.add(position_key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """抽取实体间关系"""
        relations = []
        
        # 供应关系抽取
        supply_keywords = ['供应', '提供', '生产', '制造', '销售', '采购', '购买']
        for keyword in supply_keywords:
            if keyword in text:
                # 找到关键词附近的实体
                keyword_pos = text.find(keyword)
                for i, entity1 in enumerate(entities):
                    for j, entity2 in enumerate(entities):
                        if i != j:
                            # 简单的距离判断
                            if abs(entity1['start'] - keyword_pos) < 50 and abs(entity2['start'] - keyword_pos) < 50:
                                relations.append({
                                    'source': entity1['text'],
                                    'target': entity2['text'],
                                    'relation': 'supply',
                                    'confidence': 0.7
                                })
        
        # 技术关系抽取
        tech_keywords = ['采用', '使用', '应用', '基于', '利用', '开发']
        for keyword in tech_keywords:
            if keyword in text:
                keyword_pos = text.find(keyword)
                for i, entity1 in enumerate(entities):
                    for j, entity2 in enumerate(entities):
                        if i != j and entity1['type'] == 'enterprise' and entity2['type'] == 'technology':
                            if abs(entity1['start'] - keyword_pos) < 50 and abs(entity2['start'] - keyword_pos) < 50:
                                relations.append({
                                    'source': entity1['text'],
                                    'target': entity2['text'],
                                    'relation': 'technology',
                                    'confidence': 0.8
                                })
        
        # 竞争关系抽取
        compete_keywords = ['竞争', '对手', '替代', '相比', '对比']
        for keyword in compete_keywords:
            if keyword in text:
                keyword_pos = text.find(keyword)
                for i, entity1 in enumerate(entities):
                    for j, entity2 in enumerate(entities):
                        if i != j and entity1['type'] == 'enterprise' and entity2['type'] == 'enterprise':
                            if abs(entity1['start'] - keyword_pos) < 50 and abs(entity2['start'] - keyword_pos) < 50:
                                relations.append({
                                    'source': entity1['text'],
                                    'target': entity2['text'],
                                    'relation': 'compete',
                                    'confidence': 0.6
                                })
        
        return relations

class PatentDataProcessor:
    """专利数据处理器"""
    
    def __init__(self):
        self.extractor = IndustryEntityExtractor()
    
    def generate_sample_data(self) -> List[Dict]:
        """生成模拟专利数据"""
        sample_patents = [
            {
                'id': 'CN202100001',
                'title': '一种基于5G技术的智能驾驶系统',
                'abstract': '本发明涉及一种基于5G技术的智能驾驶系统，由华为技术有限公司开发，采用人工智能算法进行环境感知和决策控制。该系统可与比亚迪股份有限公司的电动汽车平台集成，实现自动驾驶功能。相比特斯拉的自动驾驶技术，本系统在复杂路况下具有更好的适应性。',
                'applicant': '华为技术有限公司',
                'inventor': '张三;李四',
                'application_date': '2021-01-15',
                'publication_date': '2021-07-20'
            },
            {
                'id': 'CN202100002',
                'title': '新能源汽车动力电池管理系统',
                'abstract': '本发明公开了一种新能源汽车动力电池管理系统，由宁德时代新能源科技股份有限公司研发。该系统采用先进的电池技术，可为比亚迪、特斯拉等电动汽车制造商提供高性能动力电池解决方案。系统集成了物联网技术，实现电池状态的实时监控和智能管理。',
                'applicant': '宁德时代新能源科技股份有限公司',
                'inventor': '王五;赵六',
                'application_date': '2021-02-10',
                'publication_date': '2021-08-15'
            },
            {
                'id': 'CN202100003',
                'title': '柔性OLED显示屏制造工艺',
                'abstract': '本发明涉及一种柔性OLED显示屏制造工艺，由京东方科技集团股份有限公司开发。该工艺采用先进的半导体技术，生产的高质量柔性屏可供应给小米、OPPO、vivo等智能手机制造商。相比传统LCD技术，柔性OLED具有更好的显示效果和更薄的设计。',
                'applicant': '京东方科技集团股份有限公司',
                'inventor': '孙七;周八',
                'application_date': '2021-03-05',
                'publication_date': '2021-09-10'
            },
            {
                'id': 'CN202100004',
                'title': '无人机智能避障系统',
                'abstract': '本发明公开了一种无人机智能避障系统，由大疆创新科技有限公司研发。该系统基于计算机视觉和深度学习技术，能够实时识别障碍物并进行智能避障。该技术可应用于农业植保、航拍摄影等领域，为无人机行业提供安全可靠的飞行保障。',
                'applicant': '大疆创新科技有限公司',
                'inventor': '吴九;郑十',
                'application_date': '2021-04-20',
                'publication_date': '2021-10-25'
            },
            {
                'id': 'CN202100005',
                'title': '智能安防监控系统',
                'abstract': '本发明涉及一种智能安防监控系统，由海康威视数字技术股份有限公司开发。该系统集成了人工智能、物联网和大数据技术，可实现人脸识别、行为分析等功能。系统可为政府、企业、学校等机构提供全方位的安防解决方案，在深圳、北京、上海等城市得到广泛应用。',
                'applicant': '海康威视数字技术股份有限公司',
                'inventor': '陈十一;刘十二',
                'application_date': '2021-05-12',
                'publication_date': '2021-11-30'
            }
        ]
        return sample_patents
    
    def process_patents(self, patents: List[Dict]) -> Dict:
        """处理专利数据，抽取实体和关系"""
        results = {
            'patents': [],
            'entities': [],
            'relations': [],
            'statistics': {}
        }
        
        all_entities = []
        all_relations = []
        
        for patent in patents:
            # 合并标题和摘要
            text = f"{patent['title']} {patent['abstract']}"
            
            # 抽取实体
            entities = self.extractor.extract_entities(text)
            
            # 抽取关系
            relations = self.extractor.extract_relations(text, entities)
            
            # 添加专利信息
            patent_result = {
                'id': patent['id'],
                'title': patent['title'],
                'entities': entities,
                'relations': relations,
                'entity_count': len(entities),
                'relation_count': len(relations)
            }
            
            results['patents'].append(patent_result)
            all_entities.extend(entities)
            all_relations.extend(relations)
        
        # 统计信息
        entity_types = defaultdict(int)
        relation_types = defaultdict(int)
        
        for entity in all_entities:
            entity_types[entity['type']] += 1
        
        for relation in all_relations:
            relation_types[relation['relation']] += 1
        
        results['statistics'] = {
            'total_patents': len(patents),
            'total_entities': len(all_entities),
            'total_relations': len(all_relations),
            'entity_types': dict(entity_types),
            'relation_types': dict(relation_types)
        }
        
        return results

def main():
    """主函数 - 演示实体抽取功能"""
    print("=" * 60)
    print("产业知识图谱 - 实体识别与抽取Demo (简化版)")
    print("=" * 60)
    
    # 初始化处理器
    processor = PatentDataProcessor()
    
    # 生成模拟数据
    print("\n1. 生成模拟专利数据...")
    patents = processor.generate_sample_data()
    print(f"生成了 {len(patents)} 条专利数据")
    
    # 处理专利数据
    print("\n2. 开始实体抽取和关系识别...")
    results = processor.process_patents(patents)
    
    # 显示统计信息
    print("\n3. 抽取结果统计:")
    stats = results['statistics']
    print(f"   - 专利数量: {stats['total_patents']}")
    print(f"   - 实体数量: {stats['total_entities']}")
    print(f"   - 关系数量: {stats['total_relations']}")
    
    print("\n   实体类型分布:")
    for entity_type, count in stats['entity_types'].items():
        type_name = processor.extractor.entity_types.get(entity_type, entity_type)
        print(f"   - {type_name}: {count}")
    
    print("\n   关系类型分布:")
    for relation_type, count in stats['relation_types'].items():
        type_name = processor.extractor.relation_types.get(relation_type, relation_type)
        print(f"   - {type_name}: {count}")
    
    # 显示详细结果
    print("\n4. 详细抽取结果:")
    for i, patent in enumerate(results['patents'], 1):
        print(f"\n专利 {i}: {patent['id']}")
        print(f"标题: {patent['title']}")
        print(f"实体数量: {patent['entity_count']}, 关系数量: {patent['relation_count']}")
        
        if patent['entities']:
            print("  抽取的实体:")
            for entity in patent['entities']:
                type_name = processor.extractor.entity_types.get(entity['type'], entity['type'])
                print(f"    - {entity['text']} ({type_name}, 置信度: {entity['confidence']:.2f})")
        
        if patent['relations']:
            print("  识别的关系:")
            for relation in patent['relations']:
                type_name = processor.extractor.relation_types.get(relation['relation'], relation['relation'])
                print(f"    - {relation['source']} --{type_name}--> {relation['target']} (置信度: {relation['confidence']:.2f})")
    
    # 保存结果到JSON文件
    print("\n5. 保存结果到文件...")
    with open('entity_extraction_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("结果已保存到 entity_extraction_results.json")
    
    print("\n" + "=" * 60)
    print("Demo演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 