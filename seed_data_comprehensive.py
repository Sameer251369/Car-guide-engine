"""
Comprehensive seeding script for all 36 Indian states and union territories.
Run with: python seed_data_comprehensive.py
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carguide.settings')
django.setup()

from portfolio.models import Brand, Vehicle, VehicleVariant, VehicleImage
from blog.models import Category, Tag, Article
from calculator.models import State, RoadTaxSlab, InsuranceEstimate, DealerCharge


def seed_states():
    """
    Seeds all 36 Indian states and union territories with road tax data.
    Tax rates are based on 2026 estimates and typical state policies.
    """
    
    # Define all states with their configurations
    # Format: (code, name, price_basis, pre_gst_factor if applicable)
    states_data = [
        # States with Ex-Showroom pricing basis
        ("AP", "Andhra Pradesh", "ex_showroom", None),
        ("AR", "Arunachal Pradesh", "ex_showroom", None),
        ("AS", "Assam", "ex_showroom", None),
        ("BR", "Bihar", "ex_showroom", None),
        ("CG", "Chhattisgarh", "ex_showroom", None),
        ("GA", "Goa", "ex_showroom", None),
        ("HR", "Haryana", "ex_showroom", None),
        ("HP", "Himachal Pradesh", "ex_showroom", None),
        ("JH", "Jharkhand", "pre_gst", Decimal("0.7200")),
        ("KL", "Kerala", "ex_showroom", None),
        ("MP", "Madhya Pradesh", "ex_showroom", None),
        ("MN", "Manipur", "ex_showroom", None),
        ("ML", "Meghalaya", "ex_showroom", None),
        ("MZ", "Mizoram", "ex_showroom", None),
        ("NL", "Nagaland", "ex_showroom", None),
        ("OD", "Odisha", "ex_showroom", None),
        ("PB", "Punjab", "ex_showroom", None),
        ("RJ", "Rajasthan", "ex_showroom", None),
        ("SK", "Sikkim", "ex_showroom", None),
        ("TN", "Tamil Nadu", "ex_showroom", None),
        ("TG", "Telangana", "ex_showroom", None),
        ("TR", "Tripura", "ex_showroom", None),
        ("UP", "Uttar Pradesh", "ex_showroom", None),
        ("UK", "Uttarakhand", "ex_showroom", None),
        ("WB", "West Bengal", "ex_showroom", None),
        
        # Union Territories
        ("DL", "Delhi (NCT)", "ex_showroom", None),
        ("JK", "Jammu and Kashmir", "ex_showroom", None),
        ("LA", "Ladakh", "ex_showroom", None),
        ("CH", "Chandigarh (UT)", "pre_gst", Decimal("0.7200")),
        ("PY", "Puducherry", "ex_showroom", None),
        ("AN", "Andaman and Nicobar Islands", "ex_showroom", None),
        ("LD", "Lakshadweep", "ex_showroom", None),
        ("DN", "Dadra and Nagar Haveli and Daman and Diu", "ex_showroom", None),
        
        # Special: Maharashtra and Gujarat (kept with original config)
        ("MH", "Maharashtra", "ex_showroom", None),
        ("GJ", "Gujarat", "pre_gst", Decimal("0.7200")),
        ("KA", "Karnataka", "ex_showroom", None),
    ]
    
    # Standard fees applicable to all states
    standard_fees = {
        "registration_fee": Decimal("600.00"),
        "smart_card_fee": Decimal("200.00"),
        "hsrp_fee": Decimal("400.00"),
        "hypothecation_fee": Decimal("1500.00"),
        "fastag_fee": Decimal("500.00"),
    }
    
    # Road tax rates by state (simplified slabs)
    # Format: {state_code: {fuel_type: [(max_price, rate), ...]}}
    road_tax_rates = {
        # Delhi (7-11% on ex-showroom)
        "DL": {
            "petrol": [
                (Decimal("600000.00"), Decimal("0.07")),
                (Decimal("1000000.00"), Decimal("0.09")),
                (None, Decimal("0.11")),
            ],
            "diesel": [(None, Decimal("0.13"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Maharashtra (11-14% on ex-showroom)
        "MH": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.11")),
                (Decimal("2000000.00"), Decimal("0.12")),
                (None, Decimal("0.13")),
            ],
            "diesel": [(None, Decimal("0.14"))],
            "electric": [(None, Decimal("0.06"))],
        },
        # Gujarat (6% on pre-GST basis)
        "GJ": {
            "petrol": [(None, Decimal("0.06"))],
            "diesel": [(None, Decimal("0.06"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Chandigarh (8% on pre-GST basis)
        "CH": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.08"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Karnataka (13-18% on ex-showroom)
        "KA": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.13")),
                (None, Decimal("0.18")),
            ],
            "diesel": [(None, Decimal("0.18"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Jharkhand (6% on pre-GST basis)
        "JH": {
            "petrol": [(None, Decimal("0.06"))],
            "diesel": [(None, Decimal("0.06"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Rajasthan (8% on ex-showroom)
        "RJ": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Uttar Pradesh (9-11% on ex-showroom)
        "UP": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.09")),
                (None, Decimal("0.11")),
            ],
            "diesel": [(None, Decimal("0.13"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Tamil Nadu (10% on ex-showroom)
        "TN": {
            "petrol": [(None, Decimal("0.10"))],
            "diesel": [(None, Decimal("0.13"))],
            "electric": [(None, Decimal("0.02"))],
        },
        # Telangana (10% on ex-showroom)
        "TG": {
            "petrol": [(None, Decimal("0.10"))],
            "diesel": [(None, Decimal("0.12"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Punjab (9-10% on ex-showroom)
        "PB": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.09")),
                (None, Decimal("0.10")),
            ],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Haryana (9-11% on ex-showroom)
        "HR": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.09")),
                (None, Decimal("0.11")),
            ],
            "diesel": [(None, Decimal("0.13"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Madhya Pradesh (9% on ex-showroom)
        "MP": {
            "petrol": [(None, Decimal("0.09"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # West Bengal (9-10% on ex-showroom)
        "WB": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.09")),
                (None, Decimal("0.10")),
            ],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Odisha (9% on ex-showroom)
        "OD": {
            "petrol": [(None, Decimal("0.09"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Andhra Pradesh (10% on ex-showroom)
        "AP": {
            "petrol": [(None, Decimal("0.10"))],
            "diesel": [(None, Decimal("0.12"))],
            "electric": [(None, Decimal("0.02"))],
        },
        # Assam (8% on ex-showroom)
        "AS": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Kerala (11% on ex-showroom)
        "KL": {
            "petrol": [(None, Decimal("0.11"))],
            "diesel": [(None, Decimal("0.13"))],
            "electric": [(None, Decimal("0.04"))],
        },
        # Goa (9% on ex-showroom)
        "GA": {
            "petrol": [(None, Decimal("0.09"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Uttarakhand (8-9% on ex-showroom)
        "UK": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.08")),
                (None, Decimal("0.09")),
            ],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Himachal Pradesh (7-8% on ex-showroom)
        "HP": {
            "petrol": [
                (Decimal("1000000.00"), Decimal("0.07")),
                (None, Decimal("0.08")),
            ],
            "diesel": [(None, Decimal("0.09"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Jammu and Kashmir (8% on ex-showroom)
        "JK": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Ladakh (8% on ex-showroom)
        "LA": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Puducherry (9% on ex-showroom)
        "PY": {
            "petrol": [(None, Decimal("0.09"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Andaman and Nicobar Islands (8% on ex-showroom)
        "AN": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Lakshadweep (8% on ex-showroom)
        "LD": {
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Dadra and Nagar Haveli and Daman and Diu (6% on ex-showroom)
        "DN": {
            "petrol": [(None, Decimal("0.06"))],
            "diesel": [(None, Decimal("0.06"))],
            "electric": [(None, Decimal("0.00"))],
        },
        # Minor states (standardized at 8-9% for petrol)
        "AR": {  # Arunachal Pradesh
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "MN": {  # Manipur
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "ML": {  # Meghalaya
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "MZ": {  # Mizoram
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "NL": {  # Nagaland
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "SK": {  # Sikkim
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
        "TR": {  # Tripura
            "petrol": [(None, Decimal("0.08"))],
            "diesel": [(None, Decimal("0.10"))],
            "electric": [(None, Decimal("0.00"))],
        },
    }
    
    count_created = 0
    count_updated = 0
    
    for code, name, price_basis, pre_gst_factor in states_data:
        state, created = State.objects.get_or_create(
            code=code,
            defaults={
                "name": name,
                "price_basis": price_basis,
                "pre_gst_factor": pre_gst_factor or Decimal("0.7200"),
                **standard_fees,
                "is_active": True,
            }
        )
        
        if created:
            count_created += 1
            print(f"✓ Created state: {name} ({code})")
        else:
            count_updated += 1
        
        # Add road tax slabs if not already present
        rates = road_tax_rates.get(code, {
            "petrol": [(None, Decimal("0.09"))],
            "diesel": [(None, Decimal("0.11"))],
            "electric": [(None, Decimal("0.00"))],
        })
        
        for fuel_type, slabs in rates.items():
            min_price = Decimal("0")
            for max_price, rate in slabs:
                RoadTaxSlab.objects.get_or_create(
                    state=state,
                    fuel_type=fuel_type,
                    min_price=min_price,
                    max_price=max_price,
                    defaults={"rate": rate}
                )
                if max_price:
                    min_price = max_price + Decimal("0.01")
    
    print(f"\n[STATES] Created: {count_created}, Already Exist: {count_updated}")
    return count_created + count_updated


def seed_database():
    """Main seeding function."""
    print("[SEED] Seeding Car Guide Media Database...\n")
    
    # 1. Seed basic brands
    print("[BRANDS] Seeding brands...")
    tata, _ = Brand.objects.get_or_create(
        name="Tata Motors",
        defaults={
            "logo_url": "https://images.unsplash.com/photo-1617814076367-b759c7d7e738?w=300",
            "description": "India's premier automaker known for safety, EV innovation, and robust SUVs."
        }
    )
    hyundai, _ = Brand.objects.get_or_create(
        name="Hyundai",
        defaults={
            "logo_url": "https://images.unsplash.com/photo-1541348263662-e082662d82da?w=300",
            "description": "Leading global brand with feature-rich designs and premium technology."
        }
    )
    mahindra, _ = Brand.objects.get_or_create(
        name="Mahindra",
        defaults={
            "logo_url": "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=300",
            "description": "Iconic Indian SUV manufacturer built for performance and off-road capability."
        }
    )
    maruti, _ = Brand.objects.get_or_create(
        name="Maruti Suzuki",
        defaults={
            "logo_url": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=300",
            "description": "India's highest selling carmaker offering unparalleled efficiency and reach."
        }
    )
    
    # 2. Seed vehicles and variants
    print("[VEHICLES] Seeding vehicles and variants...")
    nexon_ev, _ = Vehicle.objects.get_or_create(
        slug="tata-nexon-ev",
        defaults={
            "brand": tata,
            "name": "Nexon EV",
            "body_type": "ev",
            "fuel_type": "electric",
            "ex_showroom_price": Decimal("1449000.00"),
            "starting_price": Decimal("1449000.00"),
            "top_variant_price": Decimal("1699000.00"),
            "key_specs": {
                "range": "465 km",
                "battery": "40.5 kWh",
                "power": "143 PS",
                "charging_time": "56 mins (10-80% DC)",
                "safety": "5 Star Bharat NCAP"
            },
            "is_featured": True,
            "meta_title": "Tata Nexon EV Price, Specs, On-Road Calculator | Car Guide Media",
            "meta_description": "Calculate exact on-road price for Tata Nexon EV across Delhi, Maharashtra, Gujarat and more."
        }
    )
    
    creta, _ = Vehicle.objects.get_or_create(
        slug="hyundai-creta",
        defaults={
            "brand": hyundai,
            "name": "Creta 2026",
            "body_type": "suv",
            "fuel_type": "petrol",
            "ex_showroom_price": Decimal("1099000.00"),
            "starting_price": Decimal("1099000.00"),
            "top_variant_price": Decimal("1598000.00"),
            "key_specs": {
                "engine": "1.5L Kappa Turbo GDi",
                "mileage": "17.4 kmpl",
                "power": "160 PS",
                "seating": "5 Seater",
                "features": "Level 2 ADAS, Dual Panoramic Display"
            },
            "is_featured": True,
            "meta_title": "Hyundai Creta On-Road Price Breakdown | Car Guide Media",
            "meta_description": "Explore Hyundai Creta 2026 variants, specifications, and calculate accurate on-road tax breakdown."
        }
    )
    
    thar, _ = Vehicle.objects.get_or_create(
        slug="mahindra-thar",
        defaults={
            "brand": mahindra,
            "name": "Thar ROXX 4x4",
            "body_type": "suv",
            "fuel_type": "diesel",
            "ex_showroom_price": Decimal("1299000.00"),
            "starting_price": Decimal("1299000.00"),
            "top_variant_price": Decimal("2249000.00"),
            "key_specs": {
                "engine": "2.2L mHawk Diesel",
                "power": "175 PS",
                "drivetrain": "4x4 with Terrain Response",
                "seating": "5 Seater",
                "roof": "Panoramic Skyroof"
            },
            "is_featured": True,
            "meta_title": "Mahindra Thar ROXX Price & On-Road Calculation | Car Guide Media",
            "meta_description": "Check Mahindra Thar ROXX price breakdown, road tax slabs, RTO fees and insurance."
        }
    )
    
    swift, _ = Vehicle.objects.get_or_create(
        slug="maruti-suzuki-swift",
        defaults={
            "brand": maruti,
            "name": "Swift Z-Series",
            "body_type": "hatchback",
            "fuel_type": "petrol",
            "ex_showroom_price": Decimal("649000.00"),
            "starting_price": Decimal("649000.00"),
            "top_variant_price": Decimal("964000.00"),
            "key_specs": {
                "engine": "1.2L Z-Series 3-Cyl",
                "mileage": "24.8 kmpl",
                "power": "82 PS",
                "safety": "6 Airbags Standard"
            },
            "is_featured": False,
            "meta_title": "Maruti Swift 2026 Price Breakdown | Car Guide Media",
            "meta_description": "Calculate Maruti Swift on-road price with RTO, insurance, and road tax breakdown."
        }
    )
    
    print("[INSURANCE & FEES] Seeding standard charges...")
    InsuranceEstimate.objects.get_or_create(state=None, defaults={"rate_percent": Decimal("3.50")})
    DealerCharge.objects.get_or_create(name="Standard Dealer Logistics & Handling", defaults={"amount": Decimal("1500.00"), "is_default_included": True})
    
    # 3. Seed all states and tax slabs
    print("\n[STATES & TAX SLABS] Seeding all 36 states/union territories...")
    total_states = seed_states()
    
    # 4. Seed blog content
    print("\n[BLOG] Seeding blog categories and articles...")
    buying_guides, _ = Category.objects.get_or_create(name="Buying Guides & Advice", slug="buying-guides")
    reviews, _ = Category.objects.get_or_create(name="Car Reviews & Tests", slug="car-reviews")
    
    tag_rto, _ = Tag.objects.get_or_create(name="RTO Tax", slug="rto-tax")
    tag_ev, _ = Tag.objects.get_or_create(name="EVs", slug="evs")
    
    art1, _ = Article.objects.get_or_create(
        slug="how-on-road-car-price-is-calculated-in-india-2026",
        defaults={
            "title": "Understanding On-Road Price Calculation in India: Ex-Showroom, Road Tax, RTO & TCS",
            "category": buying_guides,
            "featured_image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=1200",
            "excerpt": "Demystifying road tax slabs across all 36 states, Pre-GST calculations, 1% TCS rules, and hidden RTO costs.",
            "body": "<h3>Why On-Road Price Varies by State</h3><p>The on-road price depends on your registration state's road tax policy. Use our calculator to get exact breakdowns for all 36 Indian states and union territories.</p>",
            "author_name": "Rishabh Arora",
            "is_published": True,
            "meta_title": "How On-Road Price is Calculated in India 2026 | Car Guide Media",
            "meta_description": "Complete guide explaining RTO road tax calculation, Pre-GST state rules, TCS, and insurance estimates."
        }
    )
    art1.tags.add(tag_rto)
    
    print("\n" + "="*60)
    print("[SEED SUCCESS] Database seeded with all 36 states/UTs!")
    print("="*60)


if __name__ == '__main__':
    seed_database()
