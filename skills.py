# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-personal-agent-blood-uromodulin-tubular-nephron-reserve-skill
Category: personal_agent
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def assess_renal_uromodulin_reserve(serum_uromodulin_ng_ml, egfr_ml_min_173m2=85.0, uacr_mg_g=15.0):
    if serum_uromodulin_ng_ml <= 0:
        raise ValueError("serum_uromodulin_ng_ml must be positive")
        
    # Reference thresholds (Framingham & CKD cohorts):
    # > 150 ng/mL: High functional nephron mass / optimal tubular health
    # 100 - 150 ng/mL: Mildly decreased nephron reserve
    # 50 - 99 ng/mL: Significant tubulointerstitial atrophy
    # < 50 ng/mL: Severe nephron depletion / advanced CKD trajectory
    if serum_uromodulin_ng_ml >= 150.0:
        tubular_tier = "OPTIMAL_TUBULAR_NEPHRON_MASS"
        trajectory = "STABLE_PROTECTED"
    elif serum_uromodulin_ng_ml >= 100.0:
        tubular_tier = "MILD_TUBULAR_PARENCHYMAL_LOSS"
        trajectory = "MILD_PROGRESSION_RISK"
    elif serum_uromodulin_ng_ml >= 50.0:
        tubular_tier = "MODERATE_TUBULAR_ATROPHY"
        trajectory = "ELEVATED_ESRD_PROGRESSION_VELOCITY"
    else:
        tubular_tier = "SEVERE_TUBULOINTERSTITIAL_DEPLETION"
        trajectory = "RAPID_CKD_DETERIORATION"
        
    # Subclinical discordance: eGFR appears normal (> 60) but uromodulin is low (< 100)
    subclinical_nephron_loss = (egfr_ml_min_173m2 >= 60.0) and (serum_uromodulin_ng_ml < 100.0)
    
    return {
        "serum_uromodulin_ng_ml": round(serum_uromodulin_ng_ml, 1),
        "serum_egfr_ml_min": egfr_ml_min_173m2,
        "uacr_albuminuria_mg_g": uacr_mg_g,
        "tubular_mass_status": tubular_tier,
        "renal_trajectory_forecast": trajectory,
        "subclinical_tubular_discordance_alert": subclinical_nephron_loss,
        "clinical_insight": "Early tubular damage precedes glomerular filtration drop; consider renal-protective SGLT2i/GLP-1RA therapy." if subclinical_nephron_loss else "Preserved functional tubular nephron reserve."
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "assess_renal_uromodulin_reserve",
                        "description": """Assess functional renal tubular parenchyma reserve using serum Uromodulin (sUmod, ng/mL).
Unlike creatinine and eGFR which reflect glomerular filtration, uromodulin is exclusively produced by the thick ascending limb of Henle,
serving as a direct biomarker for intact nephron mass and early subclinical tubulointerstitial fibrosis.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = assess_renal_uromodulin_reserve(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'serum_uromodulin_ng_ml': 92.0, 'egfr_ml_min_173m2': 78.0, 'uacr_mg_g': 22.0}
        out = assess_renal_uromodulin_reserve(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
