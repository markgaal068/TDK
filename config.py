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
    "output": {
        "formats": {
            "excel": {
                "enabled": True,
                "include": ["metadata", "sections", "keywords", "tables"]
            },
            "json": {
                "enabled": True,
                "pretty_print": True
            }
        },
        "visualization": {
            "wordcloud": {
                "enabled": True,
                "width": 800,
                "height": 600
            }
        }
    },
    "system": {
        "temp_dir": "temp/",
        "log_level": "INFO"
    }
}