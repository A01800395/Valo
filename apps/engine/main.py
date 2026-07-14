from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

app = FastAPI(
    title="Valo Heuristic Pricing Engine",
    description="Deterministic parametric room rate optimization engine for independent hotels.",
    version="1.0.0"
)

# Request validation schema
class PricingRequest(BaseModel):
    rate_base: float = Field(..., gt=0, description="Base rate of the hotel room in GBP")
    occupancy_rate: float = Field(..., ge=0, le=100, description="Current occupancy percentage (0-100)")
    days_to_arrival: int = Field(..., ge=0, description="Number of days remaining to the arrival date")
    event_capacity: int = Field(..., ge=0, description="Capacity of the closest local event")
    event_distance_km: float = Field(..., ge=0, description="Distance to the closest local event venue in km")
    weather_condition: str = Field(..., description="Forecasted weather ('sunny', 'rainy', or 'normal')")
    competitor_average_rate: float = Field(..., ge=0, description="Average room rate of 5 closest competitor hotels")

# Response schema
class PricingResponse(BaseModel):
    final_rate: float
    base_rate: float
    modifiers: Dict[str, float]
    details: Dict[str, Any]
    safety_envelope_triggered: bool
    safety_message: Optional[str] = None

# Safety boundaries constant definitions
SAFETY_FLOOR_FACTOR = 0.70  # Rate cannot drop below 70% of base rate
SAFETY_CEILING_LIMIT = 280.00 # Rate cannot exceed £280.00

@app.post("/calculate-rate", response_model=PricingResponse)
def calculate_rate(request: PricingRequest):
    try:
        # 1. Event Modifier (S_event)
        s_event = 0.00
        if request.event_capacity > 20000 and request.event_distance_km <= 3.0:
            if request.event_distance_km > 0:
                s_event = min(0.40, (request.event_capacity / 100000.0) * (1.0 / request.event_distance_km))
            else:
                s_event = 0.40 # Avoid division by zero, cap at maximum modifier

        # 2. Occupancy Modifier (S_occupancy)
        s_occupancy = 0.00
        if request.occupancy_rate > 80.0 and request.days_to_arrival <= 7:
            s_occupancy = 0.20
        elif request.occupancy_rate < 30.0 and request.days_to_arrival <= 3:
            s_occupancy = -0.15

        # 3. Weather Modifier (S_weather)
        s_weather = 0.00
        if request.weather_condition.lower() == 'sunny':
            s_weather = 0.10
        elif request.weather_condition.lower() == 'rainy':
            s_weather = -0.05

        # 4. Competitor Modifier (S_competitor)
        s_competitor = 0.00
        if request.competitor_average_rate > 1.25 * request.rate_base:
            s_competitor = 0.15
        elif request.competitor_average_rate < 0.85 * request.rate_base:
            s_competitor = -0.10

        # Sum of all modifiers
        total_modifiers = s_event + s_occupancy + s_weather + s_competitor
        computed_rate = request.rate_base * (1.0 + total_modifiers)

        # 5. Apply Safety Envelopes (Floors & Ceilings)
        final_rate = computed_rate
        safety_triggered = False
        safety_msg = None
        
        floor_limit = request.rate_base * SAFETY_FLOOR_FACTOR
        
        if computed_rate < floor_limit:
            final_rate = floor_limit
            safety_triggered = True
            safety_msg = f"Rate capped at safety floor: £{floor_limit:.2f} (70% of base rate)"
        elif computed_rate > SAFETY_CEILING_LIMIT:
            final_rate = SAFETY_CEILING_LIMIT
            safety_triggered = True
            safety_msg = f"Rate capped at safety ceiling: £{SAFETY_CEILING_LIMIT:.2f}"

        return PricingResponse(
            final_rate=round(final_rate, 2),
            base_rate=request.rate_base,
            modifiers={
                "s_event": round(s_event, 4),
                "s_occupancy": round(s_occupancy, 4),
                "s_weather": round(s_weather, 4),
                "s_competitor": round(s_competitor, 4),
                "total_modifier_factor": round(total_modifiers, 4)
            },
            details={
                "raw_computed_rate": round(computed_rate, 4),
                "floor_limit": round(floor_limit, 2),
                "ceiling_limit": SAFETY_CEILING_LIMIT
            },
            safety_envelope_triggered=safety_triggered,
            safety_message=safety_msg
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "valo-pricing-engine"}
