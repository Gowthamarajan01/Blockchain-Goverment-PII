from typing import List, Dict, Any

class MaskingService:
    @staticmethod
    def mask_text(text: str, detections: List[Dict[str, Any]]) -> str:
        # Sort detections by start position in reverse to avoid index shifting
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)
        masked_text = text
        
        for det in sorted_detections:
            start = det['start']
            end = det['end']
            val = det['value']
            
            # Simple masking logic: keep last 4 chars if length > 4
            if len(val) > 4:
                # Replace everything except last 4 characters with X
                # Handling whitespace in Aadhaar etc.
                if det['type'] == "Aadhaar":
                    masked_val = "XXXX XXXX " + val[-4:]
                elif det['type'] == "PAN":
                    masked_val = "XXXXX" + val[-4:] + "X"
                else:
                    masked_val = "X" * (len(val) - 4) + val[-4:]
            else:
                masked_val = "X" * len(val)
            
            masked_text = masked_text[:start] + masked_val + masked_text[end:]
            
        return masked_text
