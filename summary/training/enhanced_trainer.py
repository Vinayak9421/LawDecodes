import sys
import os
import json
from typing import List, Dict
from transformers import T5ForConditionalGeneration, T5Tokenizer, TrainingArguments, Trainer
from datasets import Dataset
import torch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.model_config import config
# from summary.config.model_config import config


class LegalSummarizerTrainer:
    """Trainer class for T5 legal summarization"""

    def __init__(self, base_model_path: str):
        self.base_model_path = base_model_path
        print(f"🔧 Initializing trainer with model: {base_model_path}")
        
        self.tokenizer = T5Tokenizer.from_pretrained(base_model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(base_model_path)
        
        print(f"✅ Model and tokenizer loaded successfully")

    def load_training_data(self, json_files: List[str]) -> List[Dict]:
        """Load training data from multiple JSON files with flexible format handling"""
        all_examples = []
        
        for json_file in json_files:
            print(f"📁 Loading: {json_file}")

            if not os.path.exists(json_file):
                print(f"⚠️  File not found: {json_file} - Skipping")
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Handle different JSON structures
                    if 'training_examples' in data:
                        # Standard format: {"training_examples": [...]}
                        examples = data['training_examples']
                    elif isinstance(data, list):
                        # Direct list format: [...]
                        examples = data
                    else:
                        # Try to extract from other structures
                        examples = list(data.values())[0] if data else []

                    all_examples.extend(examples)
                    print(f"✅ Loaded {len(examples)} examples from {os.path.basename(json_file)}")
                    
            except Exception as e:
                print(f"❌ Error loading {json_file}: {e}")
                continue

        print(f"📊 Total training examples: {len(all_examples)}")
        return all_examples

    def validate_training_data(self, examples: List[Dict]) -> bool:
        """Validate training data structure"""
        print("🔍 Validating training data...")

        if not examples:
            print("❌ No training examples found")
            return False

        required_keys = ['legal_text', 'summary', 'section_type']
        valid_count = 0

        for i, example in enumerate(examples[:5]):  # Check first 5 examples
            missing_keys = [key for key in required_keys if key not in example]

            if not missing_keys:
                valid_count += 1
                print(f"✅ Example {i + 1}: Valid structure")
                # Show a preview of the first example
                if i == 0:
                    preview_text = example['legal_text'][:100] + "..."
                    print(f"   Preview: {preview_text}")
            else:
                print(f"⚠️  Example {i + 1}: Missing keys: {missing_keys}")
                # Try to suggest alternative keys
                available_keys = list(example.keys())
                print(f"   Available keys: {available_keys}")

        if valid_count >= 3:
            print(f"✅ Data validation passed ({valid_count}/5 examples valid)")
            return True
        else:
            print(f"❌ Data validation failed ({valid_count}/5 examples valid)")
            return False

    def format_prompts(self, examples: List[Dict]) -> List[Dict]:
        """Format examples into T5-compatible prompts"""
        formatted = []
        
        for ex in examples:
            # Create enhanced prompt for T5
            prompt = f"Summarize the following {ex['section_type']} section in simple English:\n\n{ex['legal_text']}"
            
            formatted.append({
                'input_text': prompt,
                'target_text': ex['summary'],
                'section_type': ex['section_type']
            })
        
        print(f"📝 Formatted {len(formatted)} prompts for training")
        return formatted

    def prepare_dataset(self, examples: List[Dict]) -> Dataset:
        """Prepare dataset for training"""
        def tokenize(batch):
            # Tokenize inputs
            inputs = self.tokenizer(
                batch['input_text'], 
                truncation=True, 
                padding='max_length', 
                max_length=512
            )
            
            # Tokenize targets
            labels = self.tokenizer(
                batch['target_text'], 
                truncation=True, 
                padding='max_length', 
                max_length=128
            )
            
            inputs['labels'] = labels['input_ids']
            return inputs

        dataset = Dataset.from_dict({
            'input_text': [e['input_text'] for e in examples],
            'target_text': [e['target_text'] for e in examples],
            'section_type': [e['section_type'] for e in examples]
        })
        
        tokenized_dataset = dataset.map(tokenize, batched=True)
        print(f"🔧 Dataset prepared with {len(tokenized_dataset)} examples")
        
        return tokenized_dataset

    def fine_tune(self, training_files: List[str], output_dir: str):
        """Main fine-tuning function"""
        print("🚀 Starting T5 Legal Summarization Training")
        print("=" * 50)

        # Step 1: Load training data
        examples = self.load_training_data(training_files)

        # Step 2: Validate data
        if not self.validate_training_data(examples):
            print("❌ Data validation failed. Please check your training data format.")
            return

        # Step 3: Format prompts
        formatted = self.format_prompts(examples)
        
        # Step 4: Prepare dataset
        dataset = self.prepare_dataset(formatted)

        # Step 5: Split dataset
        split_dataset = dataset.train_test_split(test_size=0.1)
        train_ds = split_dataset['train']
        eval_ds = split_dataset['test']
        
        print(f"📊 Training set: {len(train_ds)} examples")
        print(f"📊 Evaluation set: {len(eval_ds)} examples")

        # Step 6: Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/logs", exist_ok=True)

        # Step 7: Setup training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=5,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=100,
            weight_decay=0.01,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_dir=f"{output_dir}/logs",
            logging_steps=50,
            load_best_model_at_end=True,
            learning_rate=3e-5,
            report_to=None,
            save_total_limit=3,  # Keep only 3 best checkpoints
            metric_for_best_model="eval_loss",
            greater_is_better=False
        )

        # Step 8: Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=eval_ds,
            tokenizer=self.tokenizer
        )

        # Step 9: Start training
        print("🔄 Starting training...")
        print("📈 Training progress will be logged every 50 steps")
        
        trainer.train()

        # Step 10: Save final model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print("=" * 50)
        print(f"✅ Training completed! Model saved to {output_dir}")
        print(f"📁 Model files available at: {output_dir}")
        print(f"📈 Training logs available at: {output_dir}/logs")

    def test_data_loading(self, training_files: List[str]):
        """Test data loading without starting training"""
        print("🧪 Testing data loading...")
        
        examples = self.load_training_data(training_files)
        
        if self.validate_training_data(examples):
            print("✅ All data files loaded successfully!")
            print("Ready to start training.")
        else:
            print("❌ Data loading test failed.")


if __name__ == "__main__":
    import argparse
    
    # Add command line arguments for flexibility
    parser = argparse.ArgumentParser(description='Train T5 Legal Summarization Model')
    parser.add_argument('--test', action='store_true', help='Test data loading only')
    parser.add_argument('--model', default='t5-small', help='Base model to use')
    parser.add_argument('--epochs', type=int, default=5, help='Number of training epochs')
    args = parser.parse_args()

    # Configuration
    base_model = args.model
    
    data_files = [
        "../data/sample_training_data.json",
        "../data/enhanced_training_data.json",
        "../data/advance_training.json",
        "../data/advanced_training_data_final_adi.json"  # ✨ Your new training data
    ]
    
    output_model_dir = "../outputs/models/enhanced_legal_t5"

    # Initialize trainer
    trainer = LegalSummarizerTrainer(base_model)

    if args.test:
        # Test mode - just validate data loading
        trainer.test_data_loading(data_files)
    else:
        # Full training mode
        trainer.fine_tune(data_files, output_model_dir)
