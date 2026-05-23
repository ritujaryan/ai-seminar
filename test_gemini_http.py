import os
import json
import urllib.request
import urllib.error

def test_gemini():
    # Load env
    _root_dir = os.path.dirname(os.path.abspath(__file__))
    _env_path = os.path.join(_root_dir, ".env")
    if os.path.exists(_env_path):
        with open(_env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    k_str = key.strip()
                    if k_str not in os.environ:
                        os.environ[k_str] = val.strip().strip('"').strip("'")

    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("ERROR: GEMINI_API_KEY is not set.")
        return

    print(f"Testing Gemini REST API with key: {key[:8]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    
    try:
        req = urllib.request.Request(url, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            res_data = response.read().decode("utf-8")
            data = json.loads(res_data)
            print("\n[+] SUCCESS! Key is active and authorized.")
            print("Supported models:")
            for m in data.get("models", []):
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    print(f"  - {m.get('name')}")
    except urllib.error.HTTPError as e:
        print(f"\n[-] FAILED! HTTP Error Code: {e.code}")
        try:
            err_data = e.read().decode("utf-8")
            err_json = json.loads(err_data)
            print("Error Details:")
            print(json.dumps(err_json, indent=2))
        except Exception:
            print("Error Message:", e.reason)
    except Exception as e:
        print("\n[-] FAILED! Error:", e)

if __name__ == "__main__":
    test_gemini()
