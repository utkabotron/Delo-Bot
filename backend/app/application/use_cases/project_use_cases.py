from typing import Optional
from io import BytesIO
from decimal import Decimal
from app.domain.entities import Project, ProjectItem
from app.domain.repositories import IProjectRepository
from app.application.dto import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectResponseDTO,
    ProjectItemCreateDTO,
    ProjectItemResponseDTO,
    ProjectSummaryDTO,
)


class ProjectUseCases:
    def __init__(self, repository: IProjectRepository):
        self.repository = repository

    def _to_response(self, project: Project) -> ProjectResponseDTO:
        items = [
            ProjectItemResponseDTO(
                id=item.id,
                name=item.name,
                item_type=item.item_type,
                base_price=item.base_price,
                cost_price=item.cost_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
                total_cost=item.total_cost,
            )
            for item in project.items
        ]
        summary = ProjectSummaryDTO(
            subtotal=project.subtotal,
            revenue=project.revenue,
            total_cost=project.total_cost,
            profit=project.profit,
            margin=project.margin,
        )
        return ProjectResponseDTO(
            id=project.id,
            name=project.name,
            client=project.client,
            global_discount=project.global_discount,
            global_tax=project.global_tax,
            created_at=project.created_at,
            items=items,
            summary=summary,
            notes=project.notes,
            is_archived=project.is_archived,
        )

    def get_all_projects(self, archived_only: bool = False) -> list[ProjectResponseDTO]:
        projects = self.repository.get_all(archived_only=archived_only)
        return [self._to_response(p) for p in projects]

    def get_project(self, project_id: int) -> Optional[ProjectResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None
        return self._to_response(project)

    def create_project(self, dto: ProjectCreateDTO) -> ProjectResponseDTO:
        project = Project(
            name=dto.name,
            client=dto.client,
            global_discount=dto.global_discount,
            global_tax=dto.global_tax,
            notes=dto.notes,
        )
        created = self.repository.create(project)
        return self._to_response(created)

    def update_project(
        self, project_id: int, dto: ProjectUpdateDTO
    ) -> Optional[ProjectResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        if dto.name is not None:
            project.name = dto.name
        if dto.client is not None:
            project.client = dto.client
        if dto.global_discount is not None:
            project.global_discount = dto.global_discount
        if dto.global_tax is not None:
            project.global_tax = dto.global_tax
        if dto.notes is not None:
            project.notes = dto.notes
        if dto.is_archived is not None:
            project.is_archived = dto.is_archived

        updated = self.repository.update(project)
        return self._to_response(updated)

    def delete_project(self, project_id: int) -> bool:
        return self.repository.delete(project_id)

    def add_item(
        self, project_id: int, dto: ProjectItemCreateDTO
    ) -> Optional[ProjectItemResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        item = ProjectItem(
            name=dto.name,
            item_type=dto.item_type,
            base_price=dto.base_price,
            cost_price=dto.cost_price,
            quantity=dto.quantity,
        )
        created = self.repository.add_item(project_id, item)
        return ProjectItemResponseDTO(
            id=created.id,
            name=created.name,
            item_type=created.item_type,
            base_price=created.base_price,
            cost_price=created.cost_price,
            quantity=created.quantity,
            subtotal=created.subtotal,
            total_cost=created.total_cost,
        )

    def remove_item(self, item_id: int) -> bool:
        return self.repository.remove_item(item_id)

    def update_item_quantity(self, item_id: int, quantity: int) -> Optional[ProjectItemResponseDTO]:
        item = self.repository.update_item_quantity(item_id, quantity)
        if not item:
            return None
        return ProjectItemResponseDTO(
            id=item.id,
            name=item.name,
            item_type=item.item_type,
            base_price=item.base_price,
            cost_price=item.cost_price,
            quantity=item.quantity,
            subtotal=item.subtotal,
            total_cost=item.total_cost,
        )

    def _format_money(self, value: Decimal) -> str:
        return f"{float(value):,.2f}".replace(",", " ").replace(".", ",")

    def export_to_text(self, project_id: int) -> Optional[str]:
        """Export project to text format for Telegram (client version without cost/profit)"""
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        lines = []
        lines.append(f"📋 {project.name}")
        if project.client:
            lines.append(f"👤 Клиент: {project.client}")
        lines.append("")

        if project.items:
            lines.append("📦 Позиции:")
            for item in project.items:
                lines.append(
                    f"• {item.name} — {self._format_money(item.base_price)} ₽ × {item.quantity} = {self._format_money(item.subtotal)} ₽"
                )
            lines.append("")

        lines.append(f"Подытог: {self._format_money(project.subtotal)} ₽")

        if project.global_discount > 0:
            discount_amount = project.subtotal * project.global_discount / Decimal("100")
            lines.append(f"Скидка ({project.global_discount}%): -{self._format_money(discount_amount)} ₽")

        if project.global_tax > 0:
            after_discount = project.subtotal * (Decimal("1") - project.global_discount / Decimal("100"))
            tax_amount = after_discount * project.global_tax / Decimal("100")
            lines.append(f"Налог ({project.global_tax}%): -{self._format_money(tax_amount)} ₽")

        lines.append("")
        lines.append(f"💰 Итого: {self._format_money(project.revenue)} ₽")

        return "\n".join(lines)

    def export_to_pdf(self, project_id: int) -> Optional[BytesIO]:
        """Export project to PDF format for client (without cost/profit)"""
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm,
        )

        # Try to register a Cyrillic-supporting font
        font_name = "Helvetica"
        try:
            # Try common Windows font paths
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont("CyrillicFont", font_path))
                    font_name = "CyrillicFont"
                    break
        except Exception:
            pass

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontName=font_name,
            fontSize=18,
            spaceAfter=10,
        )
        normal_style = ParagraphStyle(
            "CustomNormal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11,
        )

        elements = []

        # Title
        elements.append(Paragraph(project.name, title_style))
        if project.client:
            elements.append(Paragraph(f"Клиент: {project.client}", normal_style))
        elements.append(Spacer(1, 10*mm))

        # Items table
        if project.items:
            data = [["Наименование", "Цена", "Кол-во", "Сумма"]]
            for item in project.items:
                data.append([
                    item.name,
                    f"{self._format_money(item.base_price)} ₽",
                    str(item.quantity),
                    f"{self._format_money(item.subtotal)} ₽",
                ])

            table = Table(data, colWidths=[90*mm, 30*mm, 20*mm, 30*mm])
            table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), font_name),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 5*mm))

        # Summary
        summary_data = [
            ["Подытог:", f"{self._format_money(project.subtotal)} ₽"],
        ]
        if project.global_discount > 0:
            discount_amount = project.subtotal * project.global_discount / Decimal("100")
            summary_data.append([f"Скидка ({project.global_discount}%):", f"-{self._format_money(discount_amount)} ₽"])
        if project.global_tax > 0:
            after_discount = project.subtotal * (Decimal("1") - project.global_discount / Decimal("100"))
            tax_amount = after_discount * project.global_tax / Decimal("100")
            summary_data.append([f"Налог ({project.global_tax}%):", f"-{self._format_money(tax_amount)} ₽"])
        summary_data.append(["Итого:", f"{self._format_money(project.revenue)} ₽"])

        summary_table = Table(summary_data, colWidths=[140*mm, 30*mm])
        summary_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), font_name),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, -1), (-1, -1), font_name),
            ("FONTSIZE", (0, -1), (-1, -1), 13),
            ("TOPPADDING", (0, -1), (-1, -1), 8),
        ]))
        elements.append(summary_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer
