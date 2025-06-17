from services.gemini_service import gemini_service

def test_gemini():
    # Test embedding generation
    test_text = "How do I fix a leaking hydraulic pump?"
    print("\nTesting embedding generation...")
    try:
        embedding = gemini_service.get_embedding(test_text)
        print(f"Successfully generated embedding of length: {len(embedding)}")
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return

    # Test text generation
    print("\nTesting text generation...")
    try:
        test_results = [
            {
                "title": "Hydraulic Pump Repair Guide",
                "content": "Step 1: Safety First\n- Shut down the machine\n- Relieve pressure\nStep 2: Fix leak\n- Replace seals\n- Test for leaks"
            }
        ]
        summary = gemini_service.generate_summary(test_results, test_text)
        print(f"Successfully generated summary:\n{summary}")
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return

    print("\nAll Gemini service tests passed!")

if __name__ == "__main__":
    test_gemini() 