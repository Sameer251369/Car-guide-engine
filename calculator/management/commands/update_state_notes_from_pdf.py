from django.core.management.base import BaseCommand
from pathlib import Path
import re


class Command(BaseCommand):
    help = 'Parse the Statewise PDF methodology and populate State.data_source_note for states missing notes.'

    def add_arguments(self, parser):
        parser.add_argument('--pdf', type=str, default='India_Car_Master_Database_2026_Statewise_OnRoad_Prices.pdf', help='Path to the methodology PDF')

    def handle(self, *args, **options):
        pdf_path = Path(options['pdf'])
        if not pdf_path.exists():
            self.stdout.write(self.style.ERROR(f'PDF not found at {pdf_path.resolve()}'))
            return

        # Support both older PyPDF2 and newer pypdf package names
        PdfReader = None
        try:
            from PyPDF2 import PdfReader as PdfReader_PyPDF2
            PdfReader = PdfReader_PyPDF2
        except Exception:
            try:
                from pypdf import PdfReader as PdfReader_pypdf
                PdfReader = PdfReader_pypdf
            except Exception:
                self.stdout.write(self.style.ERROR('pypdf (or PyPDF2) is required to run this command. Install with: pip install pypdf'))
                return

        reader = PdfReader(str(pdf_path))
        text_parts = []
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ''
            except Exception:
                page_text = ''
            text_parts.append(page_text)

        full_text = '\n'.join(text_parts)

        # Split into sentences for easier matching
        sentences = re.split(r'(?<=[.?!])\s+', full_text)

        from calculator.models import State

        updated = 0
        for state in State.objects.all():
            if state.data_source_note and state.data_source_note.strip():
                continue  # skip states that already have notes

            name = state.name
            code = state.code

            # Find sentences containing the state name or code (case-insensitive)
            pattern = re.compile(rf'\b({re.escape(name)}|{re.escape(code)})\b', re.IGNORECASE)
            matches = [s.strip() for s in sentences if pattern.search(s)]

            if matches:
                # Choose up to two most relevant sentences (first occurrences)
                chosen = ' '.join(matches[:2])
                summary = chosen
            else:
                # Fallback: find paragraph that mentions 'road tax' near state code/name
                idx = full_text.lower().find(name.lower())
                if idx != -1:
                    start = max(0, idx - 200)
                    end = min(len(full_text), idx + 200)
                    snippet = full_text[start:end].strip()
                    summary = snippet
                else:
                    summary = 'Estimates derived from master database methodology; see PDF for full notes.'

            # Keep summaries reasonably short
            if len(summary) > 800:
                summary = summary[:797].rsplit(' ', 1)[0] + '...'

            state.data_source_note = summary
            state.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Updated data_source_note for {updated} states.'))
