CONFIG = {
    "input": {
        "supported_formats": [".pdf", ".docx"],
        "max_file_size": 50,  # MB
        "encoding": "utf-8"
    },
    "processing": {
        "language": "auto",  # "hu", "en", or "auto"
        "sections": {
            "detect_sections": True,
            "common_headers": [
                "ABSTRACT", "INTRODUCTION", "LITERATURE REVIEW",
                "METHODOLOGY", "RESULTS", "DISCUSSION", "CONCLUSION",
                "ÖSSZEFOGLALÓ", "BEVEZETÉS", "IRODALOM ÁTTEKINTÉSE",
                "MÓDSZERTAN", "EREDMÉNYEK", "MEGBESZÉLÉS", "KÖVETKEZTETÉS"
            ]
        },
        "keywords": {
            "extraction": {
                "strategy": "combined",  # "section_only", "full_text", or "combined"
                "section_markers": {
                    "start": ["Keywords:", "Kulcsszavak:", "KEYWORDS:"],
                    "end": ["\n\n", "INTRODUCTION", "BEVEZETÉS"]
                },
                "full_text": {
                    "min_word_length": 4,
                    "max_keywords": 25,
                    "stopwords": {
                        "en": ["the", "and", "of", "in", "a", "to", "is"],
                        "hu": ["és", "a", "az", "hogy", "meg", "egy"]
                    }
                }
            },
            "weighting": {
                "section_weight": 1.5,
                "content_weight": 1.0
            }
        },
        "tables": {
            "extract": True,
            "detection_mode": "lattice"  # "stream" or "lattice"
        }
    },
    "extraction": {  # ÚJ SZEKCIÓ A HIÁNYZÓ BEÁLLÍTÁSOKKAL
        "output_file": "output/extracted_text.txt",
        "backup_dir": "output/backups/",
        "overwrite_existing": False
    },
    "output": {
        "formats": {
            "excel": {
                "enabled": True,
                "include": ["metadata", "sections", "keywords", "tables"],
                "output_path": "output/results.xlsx"  # ÚJ BEÁLLÍTÁS
            },
            "json": {
                "enabled": True,
                "pretty_print": True,
                "output_path": "output/results.json"  # ÚJ BEÁLLÍTÁS
            }
        },
        "visualization": {
            "wordcloud": {
                "enabled": True,
                "width": 800,
                "height": 600,
                "output_path": "output/wordcloud.png"  # ÚJ BEÁLLÍTÁS
            }
        }
    },
    "system": {
        "temp_dir": "temp/",
        "log_level": "INFO",
        "max_workers": 4  # ÚJ BEÁLLÍTÁS
    },
    "merging": {
    "input_dir": "./temp",
    "output_file": "./output/merged.xlsx"
},
"cleaning": {
    "output_file": "output/cleaned_data.xlsx",
    "stopwords": ["a", "an", "the", ...],
    "min_keyword_length": 4
},
}