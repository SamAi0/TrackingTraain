from decimal import Decimal
from .models import FareRule
from routes.models import RouteStation

class FareCalculationError(Exception):
    pass

def calculate_total_fare(train, source, destination, num_passengers, ticket_class):
    """
    Calculates fare based on train type, ticket class, and distance.
    Uses RouteStation to determine distance.
    Throws FareCalculationError if the fare rule is missing.
    """
    
    # 1. Determine distance
    distance = None
    try:
        src_rs = RouteStation.objects.get(route__train=train, station=source)
        dst_rs = RouteStation.objects.get(route__train=train, station=destination)
        if src_rs.distance_from_source is not None and dst_rs.distance_from_source is not None:
            distance = dst_rs.distance_from_source - src_rs.distance_from_source
            if distance < 0:
                # Reversing for safety in circular/return routes, though typically src < dst
                distance = abs(distance)
                
            if distance == 0:
                distance = 10 # minimum 10 km
    except RouteStation.DoesNotExist:
        pass

    if distance is None:
        raise FareCalculationError("Distance data is unavailable for this segment.")
        
    distance = Decimal(str(distance))

    # 2. Get applicable FareRule
    rule = FareRule.objects.filter(
        train_type=train.normalized_type,
        ticket_class=ticket_class,
        is_active=True
    ).first()

    if not rule:
        # Try finding a fallback rule for the train type with no specific class
        rule = FareRule.objects.filter(
            train_type=train.normalized_type,
            ticket_class__isnull=True,
            is_active=True
        ).first()

    if not rule:
        raise FareCalculationError(f"No active fare rule found for {train.normalized_type} class {ticket_class or 'Default'}. Please configure DEMO fare rules in the Admin panel.")

    # 3. Calculate base fare per passenger
    base_per_passenger = rule.base_fare + (distance * rule.per_km_rate)
    base_per_passenger = round(base_per_passenger, 2)
    
    total_base = base_per_passenger * Decimal(str(num_passengers))
    
    # 4. Calculate GST (5%) and Convenience Fee (Fixed 30)
    gst_amount = round(total_base * Decimal('0.05'), 2)
    fee_amount = Decimal('30.00')
    
    total_fare = total_base + gst_amount + fee_amount
    
    return {
        'base_fare': total_base,
        'gst_amount': gst_amount,
        'fee_amount': fee_amount,
        'total_fare': total_fare
    }
