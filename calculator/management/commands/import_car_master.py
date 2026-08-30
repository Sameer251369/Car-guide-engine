import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import transaction
from portfolio.models import Brand, Vehicle
from calculator.models import State, StateOnRoadPrice, VehicleStateEstimate

class Command(BaseCommand):
    help = "Idempotently import 36 states/UTs, 301 car models, and 8,428 price rows from backend/data JSON files."

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(base_dir, 'data')

        states_file = os.path.join(data_dir, 'india_states_36.json')
        if not os.path.exists(states_file):
            states_file = os.path.join(data_dir, 'india_states_28.json')
        cars_file = os.path.join(data_dir, 'india_car_models_301.json')
        master_file = os.path.join(data_dir, 'india_car_master_2026.json')

        self.stdout.write(self.style.NOTICE("Starting Car Master Database 2026 Import..."))

        with transaction.atomic():
            # 1. Import all states and union territories
            with open(states_file, 'r', encoding='utf-8') as f:
                states_data = json.load(f)

            state_code_map = {}
            states_created = 0
            states_updated = 0

            valid_codes = {s['code'].strip().upper() for s in states_data}
            State.objects.exclude(code__in=valid_codes).update(is_active=False)

            for s in states_data:
                code = s['code'].strip().upper()
                name = s['name'].strip()
                state_obj, created = State.objects.get_or_create(
                    code=code,
                    defaults={'name': name, 'is_active': True}
                )
                if created:
                    states_created += 1
                else:
                    if state_obj.name != name or not state_obj.is_active:
                        state_obj.name = name
                        state_obj.is_active = True
                        state_obj.save()
                        states_updated += 1
                state_code_map[code] = state_obj

            self.stdout.write(self.style.SUCCESS(
                f"[STATES] 36 states/UTs loaded. Created: {states_created}, Updated: {states_updated}, Active: {len(state_code_map)}"
            ))

            # 2. Import 301 Cars & Brands
            with open(cars_file, 'r', encoding='utf-8') as f:
                cars_data = json.load(f)

            vehicle_map = {} # (brand_name, car_name) -> Vehicle
            vehicles_created = 0
            vehicles_updated = 0

            for item in cars_data:
                brand_name = item['brand'].strip()
                car_name = item['car'].strip()
                body_type = item.get('body_type', 'SUV').strip()
                fuel_type = item.get('fuel', 'Petrol').strip()

                brand_slug = slugify(brand_name)
                brand_obj, _ = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={'slug': brand_slug}
                )

                fuel_lower = fuel_type.lower()
                if 'electric' in fuel_lower or fuel_lower == 'ev':
                    ev_flag = 'EV'
                elif 'hybrid' in fuel_lower:
                    ev_flag = 'Hybrid'
                elif 'cng' in fuel_lower:
                    ev_flag = 'CNG'
                else:
                    ev_flag = 'No'

                veh_slug = slugify(f"{brand_name}-{car_name}")
                veh_obj = Vehicle.objects.filter(brand=brand_obj, name=car_name).first()

                if not veh_obj:
                    veh_obj = Vehicle.objects.create(
                        brand=brand_obj,
                        name=car_name,
                        slug=veh_slug,
                        body_type=body_type,
                        fuel_type=fuel_type,
                        ev_hybrid_cng_flag=ev_flag,
                        is_active=True,
                        needs_review=False,
                        data_source='master_db_import'
                    )
                    vehicles_created += 1
                else:
                    updated = False
                    if veh_obj.body_type != body_type:
                        veh_obj.body_type = body_type
                        updated = True
                    if veh_obj.fuel_type != fuel_type:
                        veh_obj.fuel_type = fuel_type
                        updated = True
                    if veh_obj.ev_hybrid_cng_flag != ev_flag:
                        veh_obj.ev_hybrid_cng_flag = ev_flag
                        updated = True
                    if veh_obj.needs_review:
                        veh_obj.needs_review = False
                        updated = True
                    if not veh_obj.is_active:
                        veh_obj.is_active = True
                        updated = True
                    if updated:
                        veh_obj.save()
                        vehicles_updated += 1

                vehicle_map[(brand_name.lower(), car_name.lower())] = veh_obj

            self.stdout.write(self.style.SUCCESS(
                f"[CARS] 301 Unique Car Models loaded. Created: {vehicles_created}, Updated: {vehicles_updated}, Total: {len(vehicle_map)}"
            ))

            # 3. Import 8,428 State On-Road Prices using memory dict for fast upsert
            with open(master_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)

            # Pre-load existing StateOnRoadPrice objects
            existing_prices = {
                (p.car_id, p.state_id): p
                for p in StateOnRoadPrice.objects.select_related('car', 'state')
            }

            existing_estimates = {
                (e.vehicle_id, e.state_id): e
                for e in VehicleStateEstimate.objects.all()
            }

            price_rows_created = 0
            price_rows_updated = 0
            skipped_rows = 0

            to_create_prices = []
            to_update_prices = []
            to_create_estimates = []
            to_update_estimates = []

            veh_price_ranges = {} # vehicle_id -> {'start_ex': val, 'top_ex': val}

            for row in master_data:
                state_code = row['state_code'].strip().upper()
                brand_name = row['brand'].strip().lower()
                car_name = row['car'].strip().lower()

                state_obj = state_code_map.get(state_code)
                veh_obj = vehicle_map.get((brand_name, car_name))

                if not state_obj or not veh_obj:
                    skipped_rows += 1
                    continue

                start_ex = row.get('start_ex_inr')
                top_ex = row.get('top_ex_inr')
                start_otr = row.get('start_otr_inr')
                top_otr = row.get('top_otr_inr')

                if start_ex is not None and top_ex is not None:
                    if veh_obj.id not in veh_price_ranges:
                        veh_price_ranges[veh_obj.id] = {
                            'start_ex': start_ex,
                            'top_ex': top_ex
                        }

                key = (veh_obj.id, state_obj.id)
                if key in existing_prices:
                    p_obj = existing_prices[key]
                    if (p_obj.start_ex_showroom != start_ex or p_obj.top_ex_showroom != top_ex or
                        p_obj.start_on_road != start_otr or p_obj.top_on_road != top_otr):
                        p_obj.start_ex_showroom = start_ex
                        p_obj.top_ex_showroom = top_ex
                        p_obj.start_on_road = start_otr
                        p_obj.top_on_road = top_otr
                        to_update_prices.append(p_obj)
                        price_rows_updated += 1
                else:
                    to_create_prices.append(StateOnRoadPrice(
                        car=veh_obj,
                        state=state_obj,
                        start_ex_showroom=start_ex,
                        top_ex_showroom=top_ex,
                        start_on_road=start_otr,
                        top_on_road=top_otr
                    ))
                    price_rows_created += 1

                # Legacy estimates
                if start_otr is not None and top_otr is not None:
                    start_dec = Decimal(str(start_otr))
                    top_dec = Decimal(str(top_otr))
                    if key in existing_estimates:
                        e_obj = existing_estimates[key]
                        if e_obj.start_otr != start_dec or e_obj.top_otr != top_dec:
                            e_obj.start_otr = start_dec
                            e_obj.top_otr = top_dec
                            to_update_estimates.append(e_obj)
                    else:
                        to_create_estimates.append(VehicleStateEstimate(
                            vehicle=veh_obj,
                            state=state_obj,
                            start_otr=start_dec,
                            top_otr=top_dec
                        ))

            if to_create_prices:
                StateOnRoadPrice.objects.bulk_create(to_create_prices, batch_size=1000)
            if to_update_prices:
                StateOnRoadPrice.objects.bulk_update(to_update_prices, ['start_ex_showroom', 'top_ex_showroom', 'start_on_road', 'top_on_road'], batch_size=1000)

            if to_create_estimates:
                VehicleStateEstimate.objects.bulk_create(to_create_estimates, batch_size=1000)
            if to_update_estimates:
                VehicleStateEstimate.objects.bulk_update(to_update_estimates, ['start_otr', 'top_otr'], batch_size=1000)

            # Update Vehicle summary prices and is_tba flags
            tba_count = 0
            for veh in Vehicle.objects.all():
                if veh.id in veh_price_ranges:
                    p_data = veh_price_ranges[veh.id]
                    veh.starting_price = Decimal(str(p_data['start_ex']))
                    veh.top_variant_price = Decimal(str(p_data['top_ex']))
                    veh.ex_showroom_price = Decimal(str(p_data['start_ex']))
                    veh.is_tba = False
                    veh.needs_review = False
                    veh.save()
                else:
                    veh.starting_price = None
                    veh.top_variant_price = None
                    veh.ex_showroom_price = Decimal('0.00')
                    veh.is_tba = True
                    veh.needs_review = False
                    veh.save()
                    tba_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"[PRICES] Import Complete! Rows Created: {price_rows_created}, Updated: {price_rows_updated}, Skipped: {skipped_rows}. TBA Vehicles: {tba_count}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"[SUMMARY] Successfully populated {State.objects.filter(is_active=True).count()} states, {Vehicle.objects.filter(is_active=True).count()} vehicles, and {StateOnRoadPrice.objects.count()} price records."
        ))
