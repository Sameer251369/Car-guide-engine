from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from portfolio.models import Brand, Vehicle, VehicleVariant
from calculator.models import State, RoadTaxSlab, InsuranceEstimate, DealerCharge, VehicleStateEstimate, StateOnRoadPrice
from calculator.services import calculate_on_road_price
from leads.models import Lead

class RuleEnginePricingServiceTestCase(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Tata Motors", slug="tata-motors")
        
        # Vehicle <= 10L (e.g. ₹8,00,000)
        self.nexon = Vehicle.objects.create(
            brand=self.brand,
            name="Nexon",
            slug="tata-nexon",
            body_type="suv",
            fuel_type="petrol",
            ex_showroom_price=Decimal("800000.00")
        )
        
        # Vehicle > 10L (e.g. ₹15,00,000)
        self.harrier = Vehicle.objects.create(
            brand=self.brand,
            name="Harrier",
            slug="tata-harrier",
            body_type="suv",
            fuel_type="diesel",
            ex_showroom_price=Decimal("1500000.00")
        )

        # EV Vehicle
        self.nexon_ev = Vehicle.objects.create(
            brand=self.brand,
            name="Nexon EV",
            slug="tata-nexon-ev",
            body_type="ev",
            fuel_type="electric",
            ex_showroom_price=Decimal("1400000.00")
        )

        # Union Territory State (Delhi)
        self.delhi = State.objects.create(
            name="Delhi",
            code="DL",
            price_basis="ex_showroom",
            registration_fee=Decimal("600.00"),
            smart_card_fee=Decimal("200.00"),
            hsrp_fee=Decimal("400.00"),
            hypothecation_fee=Decimal("1500.00"),
            fastag_fee=Decimal("500.00")
        )
        # Delhi Petrol Individual Slab (10%)
        RoadTaxSlab.objects.create(
            state=self.delhi, fuel_type="petrol", ownership_type="individual",
            min_price=Decimal("0"), max_price=None, rate=Decimal("0.10"), cess_rate=Decimal("0.01"),
            notification_number="DL-RTO-2026/01", source_url="https://transport.delhi.gov.in"
        )
        # Delhi Petrol Company Slab (12.5%)
        RoadTaxSlab.objects.create(
            state=self.delhi, fuel_type="petrol", ownership_type="company",
            min_price=Decimal("0"), max_price=None, rate=Decimal("0.10"), company_surcharge_rate=Decimal("0.0250"),
            notification_number="DL-RTO-2026/CORP-01", source_url="https://transport.delhi.gov.in"
        )

        DealerCharge.objects.create(name="Handling Fee", amount=Decimal("1500.00"), is_default_included=True)

    def test_company_ownership_surcharge(self):
        indiv = calculate_on_road_price(self.nexon, self.delhi, fuel_type="petrol", ownership_type="individual")
        corp = calculate_on_road_price(self.nexon, self.delhi, fuel_type="petrol", ownership_type="company")

        self.assertEqual(indiv['road_tax_rate_percent'], 10.0)
        self.assertEqual(corp['road_tax_rate_percent'], 12.5)
        self.assertGreater(corp['road_tax'], indiv['road_tax'])

    def test_13_modular_charge_categories_and_subtotals(self):
        result = calculate_on_road_price(self.harrier, self.delhi, fuel_type="petrol", ownership_type="individual", is_financed=True)
        
        self.assertIn('ex_showroom_price', result)
        self.assertIn('road_tax', result)
        self.assertIn('registration_fee', result)
        self.assertIn('smart_card_fee', result)
        self.assertIn('hsrp_fee', result)
        self.assertIn('hypothecation_fee', result)
        self.assertIn('temp_registration_fee', result)
        self.assertIn('road_safety_cess', result)
        self.assertIn('green_tax', result)
        self.assertIn('municipal_cess', result)
        self.assertIn('insurance_estimate', result)
        self.assertIn('fastag_fee', result)
        self.assertIn('tcs_amount', result)

        self.assertIn('total_government_charges', result)
        self.assertIn('total_insurance', result)
        self.assertIn('optional_charges', result)
        self.assertIn('final_on_road_price', result)

    def test_rule_verification_metadata(self):
        result = calculate_on_road_price(self.nexon, self.delhi, fuel_type="petrol", ownership_type="individual")
        meta = result['rule_metadata']
        self.assertEqual(meta['notificationNumber'], 'DL-RTO-2026/01')
        self.assertEqual(meta['sourceURL'], 'https://transport.delhi.gov.in')


class CalculatorAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.brand = Brand.objects.create(name="Hyundai", slug="hyundai")
        self.vehicle = Vehicle.objects.create(
            brand=self.brand, name="Creta", slug="hyundai-creta",
            body_type="suv", fuel_type="petrol", ex_showroom_price=Decimal("1100000.00")
        )
        self.state = State.objects.create(
            name="Maharashtra", code="MH", price_basis="ex_showroom", is_active=True
        )
        RoadTaxSlab.objects.create(state=self.state, fuel_type="petrol", min_price=Decimal("0"), max_price=None, rate=Decimal("0.11"))

    def test_estimate_endpoint_with_ownership_type(self):
        payload = {
            "vehicle_id": self.vehicle.id,
            "state_id": self.state.id,
            "fuel_type": "petrol",
            "ownership_type": "company",
            "is_financed": False
        }
        response = self.client.post(reverse('calculator-estimate'), data=payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('breakdown', response.data)
        self.assertEqual(response.data['breakdown']['ownership_type'], 'company')
