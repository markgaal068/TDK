CONFIG = {
    # Fájlbeviteli beállítások
    "input": {
        "supported_formats": [".pdf", ".docx"],
        "output_dir": "output/extracted/"
    },
    
    # Letöltési beállítások
    "download": {
        "base_url": "https://tdk.uni-obuda.hu/",  # Alap URL a TDK oldalhoz
        "output_dir": "output/downloaded/",
        "max_retries": 3,
        "timeout": 30,
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        "verify_ssl": True,
        "download_delay": 1  # Másodpercek között a letöltések
    },
    
    # Feldolgozási beállítások
    "processing": {
        "keywords": {
            "extraction": {
                "section_markers": {
                    "start": ["Keywords:", "Kulcsszavak:", "Kulcsszó:", "Keywords:"],
                    "end": ["\n", "ABSTRACT", "Összefoglaló", "Summary"]
                },
                "min_length": 3,
                "max_length": 50,
                "stopwords": [
                    "és", "vagy", "de", "hogy", "mint", "amint", "amikor", "amíg", "míg",
                    "és", "vagy", "de", "hogy", "mint", "amint", "amikor", "amíg", "míg",
                    "the", "and", "or", "but", "that", "which", "when", "while", "until",
                    "this", "these", "those", "such", "so", "than", "then", "now", "here",
                    "there", "where", "why", "how", "all", "any", "both", "each", "few",
                    "more", "most", "other", "some", "such", "no", "nor", "not", "only",
                    "own", "same", "so", "than", "too", "very", "can", "will", "just",
                    "should", "now", "then", "here", "there", "where", "why", "how"
                ]
            }
        }
    },
    
    # Szövegkinyerés
    "extraction": {
        "output_file": "output/extracted_data.xlsx",
        "backup_dir": "output/backups/",
        "encoding": "utf-8",
        "max_pages": 1000,
        "min_text_length": 50
    },
    
    "merging": {
        "input_file": "output/extracted_data.xlsx",
        "output_file": "output/merged_data.xlsx",
        "backup_enabled": True,
        "remove_duplicates": True
    },
    "cleaning": {
        "input_file": "output/extracted_data.xlsx",
        "output_file": "output/cleaned_data.xlsx",
        "backup_enabled": True,
        "min_keyword_length": 4,
        "max_keyword_length": 50,
        "remove_numbers": True,
        "remove_special_chars": True,
        "normalize_case": True
    },
    "analysis": {
        "input_file": "output/extracted_data.xlsx",
        "output_file": "output/keyword_analysis.xlsx",
        "backup_enabled": True,
        "top_n": 50,
        "min_keyword_length": 3,
        "exclude_numbers": True,
        "generate_wordcloud": True,
        "wordcloud_settings": {
            "width": 800,
            "height": 600,
            "background_color": "white",
            "max_words": 100,
            "max_font_size": 150,
            "colormap": "viridis"
        },
        "generate_charts": True,
        "chart_types": ["bar", "pie"],
        "chart_settings": {
            "figsize": (12, 6),
            "dpi": 300
        }
    },
    
    # Rendszer
    "system": {
        "temp_dir": "temp/",
        "log_level": "DEBUG",
        "create_dirs": True,
        "max_workers": 4,
        "timeout": 300,
        "memory_limit": "2GB"
    }
}