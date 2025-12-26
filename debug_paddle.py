import os
# Prevent the crash
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_allocator_strategy"] = "auto_growth"

from paddleocr import PaddleOCR
import cv2

def test_paddle():
    print("--- 1. Initializing PaddleOCR (Nepali) ---")
    ocr = PaddleOCR(
        lang='ne', 
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )
    
    # Use the image visible in your screenshot
    img_path = "Darshan_front-text_block_primary_area_2.png"
    
    if not os.path.exists(img_path):
        print(f"❌ Error: Could not find image '{img_path}'")
        print("Please make sure the image file is in the same folder as this script.")
        return

    print(f"--- 2. Running Prediction on {img_path} ---")
    results = ocr.predict(img_path)
    
    print("\n--- 3. Inspecting Result Structure ---")
    print(f"Result Type: {type(results)}")
    
    if results:
        item = results[0]
        print(f"Item Type: {type(item)}")
        
        # CHECK 1: Is it a Dictionary?
        if isinstance(item, dict):
            print("✅ It is a DICTIONARY.")
            print(f"Keys: {item.keys()}")
            if 'rec_texts' in item:
                print(f"Found 'rec_texts' in dict: {item['rec_texts']}")
            else:
                print("❌ 'rec_texts' key NOT found in dict.")
        
        # CHECK 2: Is it an Object?
        else:
            print("ℹ️ It is an OBJECT (not a dict).")
            print(f"Dir: {dir(item)}")
            if hasattr(item, 'rec_texts'):
                 print(f"Found 'rec_texts' attribute: {item.rec_texts}")
            else:
                 print("❌ 'rec_texts' attribute NOT found.")

        # Print full raw content for analysis
        print("\n--- RAW CONTENT ---")
        print(item)
    else:
        print("❌ Result list is empty.")

if __name__ == "__main__":
    test_paddle()