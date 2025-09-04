import re
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'summary')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import List, Dict, Tuple
from dataclasses import dataclass


from summary.models.t5_summarizer import T5LegalSummarizer
from summary.data.preprocessor import LegalTextPreprocessor
from Extraction_Pipeline.legal_ner import LegalNER

@dataclass
class DocumentSection:
    """Represents a document section"""
    section_id: str
    title: str
    content: str
    section_type: str
    start_pos: int
    end_pos: int

class SectionWiseSummarizer:
    """Advanced section-wise legal document summarizer"""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or self._get_model_path()
        
        # Initialize components
        self.summarizer = T5LegalSummarizer(self.model_path)
        self.summarizer.load_trained_model(self.model_path)
        self.preprocessor = LegalTextPreprocessor()
        self.ner = LegalNER()
        
        print("✅ Section-wise Summarizer initialized!")
    
    def _get_model_path(self):
        """Get model path"""
        return os.path.join(os.path.dirname(__file__), '..', 'Summary', 'outputs', 'models', 'final_model')
    
    def split_document_into_sections(self, text: str) -> List[DocumentSection]:
        """Split document into logical sections"""
        sections = []
        
        # Pattern to match section headers
        section_patterns = [
            r'^(\d+\.?\s*[A-Z][^.]*?)\.?\s*$',  # "1. Introduction"
            r'^(Section\s+\d+(?:\.\d+)*\s*[^.]*?)\.?\s*$',  # "Section 1.1 Terms"
            r'^(Article\s+\d+(?:\.\d+)*\s*[^.]*?)\.?\s*$',  # "Article 1 Definitions"
            r'^(Clause\s+\d+(?:\.\d+)*\s*[^.]*?)\.?\s*$',   # "Clause 2.3 Payment"
            r'^([A-Z][A-Z\s]{3,})\s*$'  # "TERMS AND CONDITIONS"
        ]
        
        # Split text into lines
        lines = text.split('\n')
        current_section = None
        section_content = []
        section_counter = 1
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_section_header = False
            section_title = ""
            
            for pattern in section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    section_title = match.group(1).strip()
                    is_section_header = True
                    break
            
            if is_section_header and section_title:
                # Save previous section
                if current_section and section_content:
                    current_section.content = '\n'.join(section_content).strip()
                    if len(current_section.content) > 50:  # Only include substantial sections
                        sections.append(current_section)
                
                # Start new section
                current_section = DocumentSection(
                    section_id=f"section_{section_counter}",
                    title=section_title,
                    content="",
                    section_type=self._classify_section_title(section_title),
                    start_pos=i,
                    end_pos=i
                )
                section_content = []
                section_counter += 1
            else:
                # Add line to current section content
                if current_section:
                    section_content.append(line)
                    current_section.end_pos = i
                else:
                    # Create intro section for content before first header
                    if not sections and line:
                        current_section = DocumentSection(
                            section_id="section_intro",
                            title="Introduction",
                            content="",
                            section_type="introduction",
                            start_pos=0,
                            end_pos=i
                        )
                        section_content = [line]
        
        # Add final section
        if current_section and section_content:
            current_section.content = '\n'.join(section_content).strip()
            if len(current_section.content) > 50:
                sections.append(current_section)
        
        # If no sections found, treat entire document as one section
        if not sections:
            sections.append(DocumentSection(
                section_id="section_1",
                title="Complete Document",
                content=text,
                section_type="general",
                start_pos=0,
                end_pos=len(lines)
            ))
        
        return sections
    
    def _classify_section_title(self, title: str) -> str:
        """Classify section type based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['payment', 'fee', 'compensation', 'billing']):
            return 'payment'
        elif any(word in title_lower for word in ['termination', 'end', 'expiry', 'dissolution']):
            return 'termination'
        elif any(word in title_lower for word in ['liability', 'damages', 'responsible', 'indemnity']):
            return 'liability'
        elif any(word in title_lower for word in ['confidential', 'proprietary', 'non-disclosure']):
            return 'confidentiality'
        elif any(word in title_lower for word in ['conduct', 'behavior', 'ethics', 'standards']):
            return 'conduct'
        elif any(word in title_lower for word in ['intellectual', 'property', 'ip', 'copyright']):
            return 'intellectual_property'
        elif any(word in title_lower for word in ['force majeure', 'circumstances', 'events']):
            return 'force_majeure'
        elif any(word in title_lower for word in ['data', 'privacy', 'protection', 'gdpr']):
            return 'data_protection'
        else:
            return 'general'
    
    def summarize_section(self, section: DocumentSection) -> Dict:
        """Summarize individual section with NER enhancement"""
        # Extract entities
        entities = self.ner.extract_entities(section.content)
        entity_summary = self.ner.create_entity_summary(entities)
        
        # Create enhanced prompt
        enhanced_text = f"Section: {section.title}\nType: {section.section_type}\nKey Entities: {entity_summary}\n\nContent: {section.content}"
        
        formatted_prompt = f"Provide a comprehensive summary of this {section.section_type} section preserving all key legal information:\n\n{enhanced_text}"
        
        # Generate summary
        try:
            summary = self.summarizer.generate_summary(formatted_prompt, max_length=200)
            confidence = 0.95
        except Exception as e:
            print(f"⚠️ Error summarizing {section.section_id}: {e}")
            # Fallback summary
            sentences = section.content.split('.')[:3]
            summary = '. '.join([s.strip() for s in sentences if s.strip()]) + '.'
            confidence = 0.6
        
        return {
            'section_id': section.section_id,
            'title': section.title,
            'section_type': section.section_type,
            'summary': summary,
            'entities': entities,
            'entity_summary': entity_summary,
            'confidence': confidence,
            'original_length': len(section.content.split()),
            'summary_length': len(summary.split()),
            'compression_ratio': len(summary.split()) / len(section.content.split()) if section.content else 0
        }
    
    def create_executive_summary(self, section_summaries: List[Dict]) -> str:
        """Create executive summary from all sections"""
        if not section_summaries:
            return "No sections available for executive summary."
        
        # Combine key points from each section
        executive_points = []
        for section in section_summaries:
            section_summary = f"{section['title']}: {section['summary']}"
            executive_points.append(section_summary)
        
        combined_text = " | ".join(executive_points)
        
        # If combined summary is too long, create meta-summary
        if len(combined_text.split()) > 300:
            try:
                executive_prompt = f"Create an executive summary of this legal document based on these section summaries:\n\n{combined_text}"
                executive_summary = self.summarizer.generate_summary(executive_prompt, max_length=250)
                return executive_summary
            except:
                return "Multi-section legal document covering various contractual terms, obligations, and procedures as detailed in individual section summaries."
        else:
            return combined_text
    
    def process_document_sections(self, file_path: str) -> Dict:
        """Complete section-wise processing of document"""
        print(f"🔄 Processing document sections: {os.path.basename(file_path)}")
        
        # Read document
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().replace("--- Extracted Text ---", "").strip()
        except Exception as e:
            return {'error': f"Failed to read file: {e}"}
        
        if not text:
            return {'error': 'No content found in document'}
        
        # Split into sections
        sections = self.split_document_into_sections(text)
        print(f"📋 Identified {len(sections)} sections")
        
        # Summarize each section
        section_summaries = []
        for i, section in enumerate(sections, 1):
            print(f"📝 Processing section {i}/{len(sections)}: {section.title}")
            section_summary = self.summarize_section(section)
            section_summaries.append(section_summary)
        
        # Create executive summary
        executive_summary = self.create_executive_summary(section_summaries)
        
        # Compile results
        results = {
            'document_path': file_path,
            'document_name': os.path.basename(file_path),
            'total_sections': len(sections),
            'executive_summary': executive_summary,
            'section_summaries': section_summaries,
            'processing_stats': {
                'total_original_words': sum([s['original_length'] for s in section_summaries]),
                'total_summary_words': sum([s['summary_length'] for s in section_summaries]),
                'average_compression': sum([s['compression_ratio'] for s in section_summaries]) / len(section_summaries) if section_summaries else 0,
                'average_confidence': sum([s['confidence'] for s in section_summaries]) / len(section_summaries) if section_summaries else 0
            }
        }
        
        print(f"✅ Section-wise processing completed!")
        return results
    
    def save_detailed_report(self, results: Dict, output_file: str):
        """Save comprehensive section-wise report"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPREHENSIVE LEGAL DOCUMENT ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"📄 Document: {results['document_name']}\n")
            f.write(f"📊 Total Sections: {results['total_sections']}\n")
            f.write(f"📈 Average Confidence: {results['processing_stats']['average_confidence']:.2f}\n")
            f.write(f"📉 Average Compression: {results['processing_stats']['average_compression']:.2f}\n\n")
            
            f.write("🎯 EXECUTIVE SUMMARY\n")
            f.write("-" * 50 + "\n")
            f.write(f"{results['executive_summary']}\n\n")
            
            f.write("📋 SECTION-BY-SECTION ANALYSIS\n")
            f.write("-" * 50 + "\n")
            
            for i, section in enumerate(results['section_summaries'], 1):
                f.write(f"\n{i}. {section['title'].upper()}\n")
                f.write(f"   Type: {section['section_type']}\n")
                f.write(f"   Confidence: {section['confidence']:.2f}\n")
                f.write(f"   Compression: {section['original_length']} → {section['summary_length']} words\n")
                f.write(f"   Key Entities: {section['entity_summary']}\n")
                f.write(f"   Summary: {section['summary']}\n")
        
        print(f"📄 Detailed report saved to: {output_file}")

# Usage function
def process_legal_document_sections(file_path: str):
    """Main function to process document with section-wise analysis"""
    summarizer = SectionWiseSummarizer()
    results = summarizer.process_document_sections(file_path)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Display results
    print(f"\n🎯 SECTION-WISE ANALYSIS RESULTS:")
    print(f"Document: {results['document_name']}")
    print(f"Sections: {results['total_sections']}")
    print(f"Average Confidence: {results['processing_stats']['average_confidence']:.2f}")
    
    print(f"\n📊 EXECUTIVE SUMMARY:")
    print(results['executive_summary'])
    
    print(f"\n📋 INDIVIDUAL SECTIONS:")
    for section in results['section_summaries']:
        print(f"\n• {section['title']} ({section['section_type']})")
        print(f"  {section['summary']}")
        if section['entity_summary'] != "No key entities identified":
            print(f"  Key Entities: {section['entity_summary']}")
    
    # Save detailed report
    base_name, ext = os.path.splitext(file_path)
    report_file = f"{base_name}_SECTION_ANALYSIS.txt"
    summarizer.save_detailed_report(results, report_file)
    
    return results

if __name__ == "__main__":
    # Test with your extracted document
    test_file = "extracted_docx.txt"
    if os.path.exists(test_file):
        process_legal_document_sections(test_file)
    else:
        print(f"❌ File '{test_file}' not found!")
