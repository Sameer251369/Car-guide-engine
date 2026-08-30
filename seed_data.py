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

def seed_database():
    print("[SEED] Seeding Car Guide Media Database...")

    # 1. Brands
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

    # 2. Vehicles & Variants
    # Vehicle 1: Tata Nexon EV
    nexon_ev, _ = Vehicle.objects.get_or_create(
        slug="tata-nexon-ev",
        defaults={
            "brand": tata,
            "name": "Nexon EV",
            "body_type": "ev",
            "fuel_type": "electric",
            "ex_showroom_price": Decimal("1449000.00"),
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
    VehicleImage.objects.get_or_create(
        vehicle=nexon_ev,
        image_url="https://images.unsplash.com/photo-1563720223185-11003d516935?w=1000",
        defaults={"alt_text": "Tata Nexon EV Front View", "is_primary": True}
    )
    VehicleVariant.objects.get_or_create(vehicle=nexon_ev, variant_name="Creative Medium Range", defaults={"ex_showroom_price": Decimal("1449000.00"), "fuel_type": "electric"})
    VehicleVariant.objects.get_or_create(vehicle=nexon_ev, variant_name="Empowered+ Long Range", defaults={"ex_showroom_price": Decimal("1699000.00"), "fuel_type": "electric"})

    # Vehicle 2: Hyundai Creta
    creta, _ = Vehicle.objects.get_or_create(
        slug="hyundai-creta",
        defaults={
            "brand": hyundai,
            "name": "Creta 2026",
            "body_type": "suv",
            "fuel_type": "petrol",
            "ex_showroom_price": Decimal("1099000.00"),
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
    VehicleImage.objects.get_or_create(
        vehicle=creta,
        image_url="https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=1000",
        defaults={"alt_text": "Hyundai Creta Exterior", "is_primary": True}
    )
    VehicleVariant.objects.get_or_create(vehicle=creta, variant_name="E 1.5 Petrol MT", defaults={"ex_showroom_price": Decimal("1099000.00"), "fuel_type": "petrol"})
    VehicleVariant.objects.get_or_create(vehicle=creta, variant_name="SX Tech 1.5 Petrol IVT", defaults={"ex_showroom_price": Decimal("1598000.00"), "fuel_type": "petrol"})
    VehicleVariant.objects.get_or_create(vehicle=creta, variant_name="SX (O) 1.5 Diesel AT", defaults={"ex_showroom_price": Decimal("1999000.00"), "fuel_type": "diesel"})

    # Vehicle 3: Mahindra Thar
    thar, _ = Vehicle.objects.get_or_create(
        slug="mahindra-thar",
        defaults={
            "brand": mahindra,
            "name": "Thar ROXX 4x4",
            "body_type": "suv",
            "fuel_type": "diesel",
            "ex_showroom_price": Decimal("1299000.00"),
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
    VehicleImage.objects.get_or_create(
        vehicle=thar,
        image_url="https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?w=1000",
        defaults={"alt_text": "Mahindra Thar ROXX Off-roading", "is_primary": True}
    )
    VehicleVariant.objects.get_or_create(vehicle=thar, variant_name="MX1 Petrol RWD", defaults={"ex_showroom_price": Decimal("1299000.00"), "fuel_type": "petrol"})
    VehicleVariant.objects.get_or_create(vehicle=thar, variant_name="AX7L Diesel 4x4 AT", defaults={"ex_showroom_price": Decimal("2249000.00"), "fuel_type": "diesel"})

    # Vehicle 4: Maruti Suzuki Swift
    swift, _ = Vehicle.objects.get_or_create(
        slug="maruti-suzuki-swift",
        defaults={
            "brand": maruti,
            "name": "Swift Z-Series",
            "body_type": "hatchback",
            "fuel_type": "petrol",
            "ex_showroom_price": Decimal("649000.00"),
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
    VehicleImage.objects.get_or_create(
        vehicle=swift,
        image_url="https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?w=1000",
        defaults={"alt_text": "Maruti Suzuki Swift Front View", "is_primary": True}
    )
    VehicleVariant.objects.get_or_create(vehicle=swift, variant_name="LXi 1.2 MT", defaults={"ex_showroom_price": Decimal("649000.00"), "fuel_type": "petrol"})
    VehicleVariant.objects.get_or_create(vehicle=swift, variant_name="ZXi+ Dual Tone AMT", defaults={"ex_showroom_price": Decimal("964000.00"), "fuel_type": "petrol"})

    # 3. States & Tax Slabs
    # Delhi (DL) - Ex-showroom basis
    dl, _ = State.objects.get_or_create(
        code="DL",
        defaults={
            "name": "Delhi (NCT)",
            "price_basis": "ex_showroom",
            "registration_fee": Decimal("600.00"),
            "smart_card_fee": Decimal("200.00"),
            "hsrp_fee": Decimal("400.00"),
            "hypothecation_fee": Decimal("1500.00"),
            "fastag_fee": Decimal("500.00"),
            "is_active": True
        }
    )
    RoadTaxSlab.objects.get_or_create(state=dl, fuel_type="petrol", min_price=Decimal("0"), max_price=Decimal("600000.00"), defaults={"rate": Decimal("0.07")})
    RoadTaxSlab.objects.get_or_create(state=dl, fuel_type="petrol", min_price=Decimal("600000.01"), max_price=Decimal("1000000.00"), defaults={"rate": Decimal("0.09")})
    RoadTaxSlab.objects.get_or_create(state=dl, fuel_type="petrol", min_price=Decimal("1000000.01"), max_price=None, defaults={"rate": Decimal("0.11")})
    RoadTaxSlab.objects.get_or_create(state=dl, fuel_type="diesel", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.13")})
    RoadTaxSlab.objects.get_or_create(state=dl, fuel_type="electric", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.00")})

    # Maharashtra (MH) - Ex-showroom basis
    mh, _ = State.objects.get_or_create(
        code="MH",
        defaults={
            "name": "Maharashtra",
            "price_basis": "ex_showroom",
            "registration_fee": Decimal("600.00"),
            "smart_card_fee": Decimal("200.00"),
            "hsrp_fee": Decimal("500.00"),
            "hypothecation_fee": Decimal("1500.00"),
            "fastag_fee": Decimal("500.00"),
            "is_active": True
        }
    )
    RoadTaxSlab.objects.get_or_create(state=mh, fuel_type="petrol", min_price=Decimal("0"), max_price=Decimal("1000000.00"), defaults={"rate": Decimal("0.11")})
    RoadTaxSlab.objects.get_or_create(state=mh, fuel_type="petrol", min_price=Decimal("1000000.01"), max_price=Decimal("2000000.00"), defaults={"rate": Decimal("0.12")})
    RoadTaxSlab.objects.get_or_create(state=mh, fuel_type="petrol", min_price=Decimal("2000000.01"), max_price=None, defaults={"rate": Decimal("0.13")})
    RoadTaxSlab.objects.get_or_create(state=mh, fuel_type="diesel", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.14")})
    RoadTaxSlab.objects.get_or_create(state=mh, fuel_type="electric", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.06")})

    # Gujarat (GJ) - Pre-GST Basis
    gj, _ = State.objects.get_or_create(
        code="GJ",
        defaults={
            "name": "Gujarat",
            "price_basis": "pre_gst",
            "pre_gst_factor": Decimal("0.7200"),
            "registration_fee": Decimal("600.00"),
            "smart_card_fee": Decimal("200.00"),
            "hsrp_fee": Decimal("400.00"),
            "hypothecation_fee": Decimal("1500.00"),
            "fastag_fee": Decimal("500.00"),
            "is_active": True
        }
    )
    RoadTaxSlab.objects.get_or_create(state=gj, fuel_type="all", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.06")})
    RoadTaxSlab.objects.get_or_create(state=gj, fuel_type="electric", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.00")})

    # Chandigarh (CH) - Pre-GST Basis
    ch, _ = State.objects.get_or_create(
        code="CH",
        defaults={
            "name": "Chandigarh (UT)",
            "price_basis": "pre_gst",
            "pre_gst_factor": Decimal("0.7200"),
            "registration_fee": Decimal("600.00"),
            "smart_card_fee": Decimal("200.00"),
            "hsrp_fee": Decimal("400.00"),
            "hypothecation_fee": Decimal("1500.00"),
            "fastag_fee": Decimal("500.00"),
            "is_active": True
        }
    )
    RoadTaxSlab.objects.get_or_create(state=ch, fuel_type="all", min_price=Decimal("0"), max_price=None, defaults={"rate": Decimal("0.08")})

    # Karnataka (KA) - Ex-showroom basis
    ka, _ = State.objects.get_or_create(
        code="KA",
        defaults={
            "name": "Karnataka",
            "price_basis": "ex_showroom",
            "registration_fee": Decimal("600.00"),
            "smart_card_fee": Decimal("200.00"),
            "hsrp_fee": Decimal("400.00"),
            "hypothecation_fee": Decimal("1500.00"),
            "fastag_fee": Decimal("500.00"),
            "is_active": True
        }
    )
    RoadTaxSlab.objects.get_or_create(state=ka, fuel_type="petrol", min_price=Decimal("0"), max_price=Decimal("1000000.00"), defaults={"rate": Decimal("0.13")})
    RoadTaxSlab.objects.get_or_create(state=ka, fuel_type="petrol", min_price=Decimal("1000000.01"), max_price=None, defaults={"rate": Decimal("0.18")})

    # 4. Insurance & Dealer Charges
    InsuranceEstimate.objects.get_or_create(state=None, defaults={"rate_percent": Decimal("3.50")})
    DealerCharge.objects.get_or_create(name="Standard Dealer Logistics & Handling", defaults={"amount": Decimal("1500.00"), "is_default_included": True})

    # 5. Blog Categories, Tags, Articles
    news, _ = Category.objects.get_or_create(name="Automotive News", slug="automotive-news")
    reviews, _ = Category.objects.get_or_create(name="Car Reviews & Tests", slug="car-reviews")
    buying_guides, _ = Category.objects.get_or_create(name="Buying Guides & Advice", slug="buying-guides")

    tag_ev, _ = Tag.objects.get_or_create(name="EVs", slug="evs")
    tag_suv, _ = Tag.objects.get_or_create(name="SUVs", slug="suvs")
    tag_rto, _ = Tag.objects.get_or_create(name="RTO Tax", slug="rto-tax")

    art1, _ = Article.objects.get_or_create(
        slug="how-on-road-car-price-is-calculated-in-india-2026",
        defaults={
            "title": "Understanding On-Road Price Calculation in India: Ex-Showroom, Road Tax, RTO & TCS",
            "category": buying_guides,
            "featured_image_url": "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=1200",
            "excerpt": "Demystifying road tax slabs, Pre-GST calculations in Gujarat/Chandigarh, 1% TCS rules, and hidden RTO costs when buying your new car.",
            "body": """
            <h3>Why Ex-Showroom Price is Not What You Pay</h3>
            <p>When buying a new car in India, the price advertised by carmakers is the <b>ex-showroom price</b>. However, driving the vehicle legally out of the dealership requires registering it with your state RTO and securing mandatory insurance coverage.</p>

            <h3>Key On-Road Price Components</h3>
            <ul>
                <li><b>Ex-Showroom Price:</b> Base factory cost including GST and central excise.</li>
                <li><b>Road Tax (State RTO Tax):</b> Computed based on state policies. States like Delhi apply 7–11%, whereas Maharashtra applies up to 13–14%. In states like <i>Gujarat, Chandigarh, and Jharkhand</i>, road tax is levied on the <b>Pre-GST price basis</b>, significantly lowering your tax burden!</li>
                <li><b>RTO Registration & Statutory Charges:</b> Includes flat fees for registration (₹600), smart card RC (₹200), high-security registration plates (HSRP), and hypothecation charge (₹1,500) if financed.</li>
                <li><b>TCS (Tax Collected at Source):</b> A mandatory central government tax of <b>1%</b> applied on all vehicles exceeding ₹10,000,000 (₹10 Lakhs) ex-showroom price.</li>
                <li><b>Insurance Estimate:</b> Typically ~3.5% of ex-showroom value for 1-year comprehensive + 3-year third-party cover.</li>
            </ul>

            <p>Use the <b>Car Guide Media On-Road Price Calculator</b> to get instant, accurate, itemized breakdowns tailored to your state!</p>
            """,
            "author_name": "Rishabh Arora",
            "is_published": True,
            "meta_title": "How On-Road Price is Calculated in India 2026 | Car Guide Media",
            "meta_description": "Complete guide explaining RTO road tax calculation, Pre-GST state rules, TCS, and insurance estimates."
        }
    )
    art1.tags.add(tag_rto, tag_suv)

    art2, _ = Article.objects.get_or_create(
        slug="tata-nexon-ev-long-term-review-2026",
        defaults={
            "title": "Tata Nexon EV Real-World Test: Range, Charging Speed & State Subsidies Explained",
            "category": reviews,
            "featured_image_url": "https://images.unsplash.com/photo-1563720223185-11003d516935?w=1200",
            "excerpt": "We test the updated Nexon EV across 1,500 km of city traffic and highway driving to see if electric mobility makes economic sense.",
            "body": """
            <h3>The EV Advantage on Road Tax</h3>
            <p>Electric Vehicles benefit from massive road tax concessions across Indian states. In states like Delhi, Gujarat, and Rajasthan, road tax is <b>0%</b>, saving EV buyers over ₹1.5 to ₹2.5 Lakhs compared to equivalent petrol SUVs.</p>
            """,
            "author_name": "Editorial Team",
            "is_published": True,
            "meta_title": "Tata Nexon EV Real World Review & Tax Benefits | Car Guide Media",
            "meta_description": "Detailed real-world review of Tata Nexon EV featuring charging times, range, and 0% road tax savings."
        }
    )
    art2.tags.add(tag_ev)

    print("[SEED SUCCESS] Seed script completed successfully!")

if __name__ == '__main__':
    seed_database()
