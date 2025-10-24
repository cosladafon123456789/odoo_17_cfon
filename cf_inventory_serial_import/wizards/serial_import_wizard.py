# 3) Verificar si el IMEI está disponible para mover
# Solo se considerará duplicado si está reservado en otro picking ACTIVO
mls = MoveLine.search([
    ("lot_id", "=", lot.id),
    ("picking_id", "!=", picking.id),
    ("state", "not in", ["cancel", "done"])
], limit=1)

if mls:
    duplicated.append(imei)
    continue

# 4) Comprobar si tiene stock disponible en WH/Stock
domain_quant = [
    ("lot_id", "=", lot.id),
    ("location_id", "=", loc_src.id),
]
if picking.company_id:
    domain_quant.append(("company_id", "=", picking.company_id.id))

quants = Quant.search(domain_quant)
available = 0.0
for q in quants:
    available += max(q.quantity - q.reserved_quantity, 0.0)

if available <= 0:
    not_in_wh.append(imei)
    continue
