import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List


def send_welcome_email(full_name: str, recipient: str) -> None:
    """Send a branded welcome email to a newly registered user."""
    app_url  = os.getenv("APP_URL", "http://localhost:8000")
    first    = full_name.split()[0] if full_name else "there"

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">

        <!-- HEADER BANNER -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 40%,#0f3460 70%,#533483 100%);padding:44px 40px 36px;text-align:center">
            <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 20px"><tr><td style="background:rgba(255,255,255,0.15);border:2px solid rgba(255,255,255,0.35);border-radius:18px;padding:13px 24px;font-size:17px;font-weight:900;color:#ffffff;font-family:'Segoe UI',Inter,sans-serif;letter-spacing:-0.3px">&#128722;&nbsp;EcomInventory Pro</td></tr></table>
            <h1 style="color:#ffffff;font-size:26px;font-weight:800;margin:0 0 6px;letter-spacing:-0.3px">Welcome to EcomInventory Pro!</h1>
            <p style="color:rgba(255,255,255,0.70);font-size:14px;margin:0">Your account is ready &#x2705;</p>
          </td>
        </tr>

        <!-- GREETING -->
        <tr>
          <td style="padding:36px 40px 0">
            <p style="color:#1a1a2e;font-size:18px;font-weight:700;margin:0 0 10px">Hey {first}! 👋</p>
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 28px">
              You've successfully joined <strong style="color:#6C63FF">EcomInventory Pro</strong> — a modern inventory
              and commerce management platform built for growing businesses in Sierra Leone.
            </p>
          </td>
        </tr>

        <!-- FEATURES CARD -->
        <tr>
          <td style="padding:0 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9ff;border-radius:14px;padding:22px 24px">
              <tr><td>
                <p style="color:#6C63FF;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px;margin:0 0 16px">What you can do on the platform</p>
                <table cellpadding="0" cellspacing="0">
                  <tr><td style="padding:5px 0"><span style="font-size:16px">🛍️</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Browse products and place orders instantly</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">📦</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Track your orders from pending to delivered</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">🏷️</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Use voucher codes for exclusive discounts</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">⭐</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Rate & review products after delivery</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">🔐</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Secure JWT-authenticated account</span></td></tr>
                </table>
              </td></tr>
            </table>
          </td>
        </tr>

        <!-- CTA BUTTON -->
        <tr>
          <td style="padding:32px 40px;text-align:center">
            <a href="{app_url}" style="display:inline-block;background:linear-gradient(135deg,#6C63FF,#5a52d5);color:#ffffff;text-decoration:none;padding:16px 44px;border-radius:12px;font-size:16px;font-weight:700;letter-spacing:0.2px;box-shadow:0 8px 28px rgba(108,99,255,0.40)">
              Explore Your Dashboard &nbsp;→
            </a>
            <p style="color:#94a3b8;font-size:12px;margin:16px 0 0">
              Or copy this link: <a href="{app_url}" style="color:#6C63FF">{app_url}</a>
            </p>
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0;margin:0"></td></tr>

        <!-- FOOTER -->
        <tr>
          <td style="padding:24px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:12px;line-height:1.6;margin:0">
              <strong>Group D · PROG315</strong> — Limkokwing University of Creative Technology, Sierra Leone<br>
              Supporting <strong>SDG 8</strong> – Decent Work and Economic Growth
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    send_email(
        subject=f"Welcome to EcomInventory Pro, {first}!",
        html_body=html_body,
        recipient=recipient,
    )


def send_seller_welcome_email(full_name: str, email: str, shop_name: str, what_you_sell: str = None, location: str = None) -> None:
    """Send a branded welcome email specifically for new sellers."""
    app_url = os.getenv("APP_URL", "http://localhost:8000")
    first   = full_name.split()[0] if full_name else "there"
    details_rows = ""
    if shop_name:
        details_rows += f'<tr><td style="padding:5px 0"><span style="font-size:16px">🏪</span>&nbsp;&nbsp;<strong style="color:#1a1a2e">{shop_name}</strong> — your shop name</td></tr>'
    if what_you_sell:
        details_rows += f'<tr><td style="padding:5px 0"><span style="font-size:16px">📦</span>&nbsp;&nbsp;<span style="color:#1a1a2e">You sell: {what_you_sell}</span></td></tr>'
    if location:
        details_rows += f'<tr><td style="padding:5px 0"><span style="font-size:16px">📍</span>&nbsp;&nbsp;<span style="color:#1a1a2e">Based in: {location}</span></td></tr>'

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">

        <!-- HEADER BANNER -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 35%,#0f3460 65%,#533483 100%);padding:44px 40px 36px;text-align:center">
            <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 20px"><tr><td style="background:rgba(255,255,255,0.15);border:2px solid rgba(255,255,255,0.35);border-radius:18px;padding:13px 24px;font-size:17px;font-weight:900;color:#ffffff;font-family:'Segoe UI',Inter,sans-serif;letter-spacing:-0.3px">&#128722;&nbsp;EcomInventory Pro</td></tr></table>
            <h1 style="color:#ffffff;font-size:26px;font-weight:800;margin:0 0 6px;letter-spacing:-0.3px">Welcome, Seller! 🏪</h1>
            <p style="color:rgba(255,255,255,0.70);font-size:14px;margin:0">Your shop is live on EcomInventory Pro ✅</p>
          </td>
        </tr>

        <!-- GREETING -->
        <tr>
          <td style="padding:36px 40px 0">
            <p style="color:#1a1a2e;font-size:18px;font-weight:700;margin:0 0 10px">Hey {first}! 👋</p>
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 24px">
              You've successfully registered as a <strong style="color:#f39c12">Seller</strong> on
              <strong style="color:#6C63FF">EcomInventory Pro</strong>. Your shop is ready —
              log in to start adding products and reaching customers across Sierra Leone.
            </p>
          </td>
        </tr>

        <!-- SHOP DETAILS -->
        {f'''<tr>
          <td style="padding:0 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#fff8ed,#fff3e0);border:1.5px solid #f39c12;border-radius:14px;padding:20px 22px">
              <tr><td>
                <p style="color:#b07d0a;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px;margin:0 0 12px">Your Seller Details</p>
                <table cellpadding="0" cellspacing="0">{details_rows}</table>
              </td></tr>
            </table>
          </td>
        </tr>''' if details_rows else ''}

        <!-- WHAT YOU CAN DO -->
        <tr>
          <td style="padding:24px 40px 0">
            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9ff;border-radius:14px;padding:22px 24px">
              <tr><td>
                <p style="color:#6C63FF;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px;margin:0 0 16px">What you can do as a Seller</p>
                <table cellpadding="0" cellspacing="0">
                  <tr><td style="padding:5px 0"><span style="font-size:16px">➕</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Add and manage your own products</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">🗂️</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Organise products by category</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">📧</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Customers get notified by email when you add a product</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">⭐</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Customers can rate and review your products</span></td></tr>
                  <tr><td style="padding:5px 0"><span style="font-size:16px">📊</span>&nbsp;&nbsp;<span style="color:#1a1a2e;font-size:14px">Track orders and revenue from your dashboard</span></td></tr>
                </table>
              </td></tr>
            </table>
          </td>
        </tr>

        <!-- CTA SECTION -->
        <tr>
          <td style="padding:36px 40px 32px;text-align:center">
            <p style="color:#64748b;font-size:13px;margin:0 0 22px;line-height:1.6">
              Everything is set up and ready for you.<br>
              Click below to sign in and start building your shop.
            </p>

            <!-- Primary button -->
            <a href="{app_url}" style="
              display:inline-block;
              background:linear-gradient(135deg,#f39c12 0%,#e67e22 100%);
              color:#ffffff;
              text-decoration:none;
              padding:17px 48px;
              border-radius:14px;
              font-size:16px;
              font-weight:800;
              letter-spacing:0.3px;
              box-shadow:0 10px 32px rgba(243,156,18,0.45), 0 2px 8px rgba(0,0,0,0.12);
              line-height:1;
            ">
              🚀 &nbsp;Explore Your Seller Dashboard
            </a>

            <!-- Secondary text link -->
            <p style="margin:18px 0 0;font-size:12px;color:#94a3b8">
              Or paste this link in your browser:&nbsp;
              <a href="{app_url}" style="color:#6C63FF;font-weight:600;text-decoration:none">{app_url}</a>
            </p>

            <!-- Trust line -->
            <p style="margin:24px 0 0;font-size:11px;color:#cbd5e1;letter-spacing:0.3px">
              🔒 &nbsp;Secured with JWT authentication &nbsp;·&nbsp; Session expires in 30 minutes
            </p>
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0;margin:0"></td></tr>

        <!-- FOOTER -->
        <tr>
          <td style="padding:24px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:12px;line-height:1.6;margin:0">
              <strong>Group D · PROG315</strong> — Limkokwing University of Creative Technology, Sierra Leone<br>
              Supporting <strong>SDG 8</strong> – Decent Work and Economic Growth
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    send_email(
        subject=f"🏪 Welcome to EcomInventory Pro, {first}! Your shop '{shop_name}' is live",
        html_body=html_body,
        recipient=email,
    )


def send_new_product_email(product_name: str, shop_name: str, product_id: int, recipients: List[str]) -> None:
    """Notify all customers that a new product has been added."""
    app_url = os.getenv("APP_URL", "http://localhost:8000")
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 40%,#0f3460 70%,#533483 100%);padding:40px;text-align:center">
            <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px"><tr><td style="background:rgba(255,255,255,0.15);border:2px solid rgba(255,255,255,0.35);border-radius:16px;padding:11px 20px;font-size:15px;font-weight:900;color:#ffffff;font-family:'Segoe UI',Inter,sans-serif;letter-spacing:-0.3px">&#128722;&nbsp;EcomInventory Pro</td></tr></table>
            <h1 style="color:#fff;font-size:22px;font-weight:800;margin:0 0 6px">New Product Arrival! 🎉</h1>
            <p style="color:rgba(255,255,255,0.7);font-size:13px;margin:0">Fresh from <strong style="color:#a78bfa">{shop_name}</strong></p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px">
            <p style="color:#1a1a2e;font-size:17px;font-weight:700;margin:0 0 10px">✨ {product_name}</p>
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 28px">
              A new product has just landed on <strong style="color:#6C63FF">EcomInventory Pro</strong>!
              Head over to the dashboard to check it out before it sells out.
            </p>
            <div style="text-align:center">
              <a href="{app_url}" style="display:inline-block;background:linear-gradient(135deg,#6C63FF,#5a52d5);color:#fff;text-decoration:none;padding:14px 40px;border-radius:12px;font-size:15px;font-weight:700;box-shadow:0 6px 22px rgba(108,99,255,0.4)">
                Explore Now &nbsp;→
              </a>
            </div>
          </td>
        </tr>
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0"></td></tr>
        <tr>
          <td style="padding:20px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:11px;margin:0">Group D · PROG315 — Limkokwing University, Sierra Leone · SDG 8</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    for recipient in recipients:
        send_email(
            subject=f"New Arrival: {product_name} from {shop_name}",
            html_body=html_body,
            recipient=recipient,
        )


def send_voucher_email(code: str, discount_type: str, discount_value: float, recipients: List[str]) -> None:
    """Blast a voucher code to a list of users."""
    app_url = os.getenv("APP_URL", "http://localhost:8000")
    if discount_type == "percentage":
        discount_label = f"{int(discount_value)}% OFF"
    else:
        discount_label = f"Le {discount_value:.2f} OFF"

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">
        <tr>
          <td style="background:linear-gradient(135deg,#f39c12 0%,#e67e22 100%);padding:40px;text-align:center">
            <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px"><tr><td style="background:rgba(255,255,255,0.20);border:2px solid rgba(255,255,255,0.40);border-radius:16px;padding:11px 20px;font-size:15px;font-weight:900;color:#ffffff;font-family:'Segoe UI',Inter,sans-serif;letter-spacing:-0.3px">&#128722;&nbsp;EcomInventory Pro</td></tr></table>
            <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0 0 6px">🏷️ Your Discount is Ready!</h1>
            <p style="color:rgba(255,255,255,0.85);font-size:13px;margin:0">Exclusive offer just for you</p>
          </td>
        </tr>
        <tr>
          <td style="padding:36px 40px;text-align:center">
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 24px">
              Use the code below at checkout to save <strong style="color:#f39c12">{discount_label}</strong> on your next order.
            </p>
            <div style="background:#fff8ed;border:2px dashed #f39c12;border-radius:14px;padding:22px 30px;margin:0 0 28px;display:inline-block">
              <p style="color:#94a3b8;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px">Your Voucher Code</p>
              <p style="color:#1a1a2e;font-size:32px;font-weight:800;font-family:monospace;letter-spacing:4px;margin:0">{code}</p>
              <p style="color:#f39c12;font-size:14px;font-weight:700;margin:8px 0 0">{discount_label}</p>
            </div>
            <div style="text-align:center">
              <a href="{app_url}" style="display:inline-block;background:linear-gradient(135deg,#f39c12,#e67e22);color:#fff;text-decoration:none;padding:14px 40px;border-radius:12px;font-size:15px;font-weight:700;box-shadow:0 6px 22px rgba(243,156,18,0.4)">
                Grab Your Discount &nbsp;→
              </a>
            </div>
          </td>
        </tr>
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0"></td></tr>
        <tr>
          <td style="padding:20px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:11px;margin:0">Group D · PROG315 — Limkokwing University, Sierra Leone · SDG 8</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
    for recipient in recipients:
        send_email(
            subject=f"🏷️ Your {discount_label} voucher code: {code}",
            html_body=html_body,
            recipient=recipient,
        )


def send_order_confirmation_email(
    customer_name: str,
    customer_email: str,
    order_id: int,
    items: list,          # list of dicts: {name, qty, unit_price, shop_name}
    total: float,
    discount: float = 0.0,
    voucher_code: str = None,
) -> None:
    """Send a branded order confirmation / thank-you email to the customer."""
    app_url  = os.getenv("APP_URL", "http://localhost:8000")
    first    = customer_name.split()[0] if customer_name else "there"
    subtotal = total + discount

    rows = "".join(
        f"""<tr>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0">
            <strong style="color:#1a1a2e;font-size:14px">{item['name']}</strong>
            <br><span style="color:#94a3b8;font-size:12px">from {item.get('shop_name','EcomInventory Pro')}</span>
          </td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;color:#64748b;font-size:13px">x{item['qty']}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:right;font-weight:700;color:#1a1a2e;font-size:14px">${item['unit_price']*item['qty']:.2f}</td>
        </tr>"""
        for item in items
    )
    discount_row = f"""<tr>
      <td colspan="2" style="padding:8px 14px;text-align:right;color:#2ecc71;font-size:13px;font-weight:600">
        Voucher ({voucher_code}) —
      </td>
      <td style="padding:8px 14px;text-align:right;color:#2ecc71;font-size:14px;font-weight:700">-${discount:.2f}</td>
    </tr>""" if discount > 0 else ""

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">

        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#0f172a 0%,#1a2744 50%,#1e3a5f 100%);padding:44px 40px 36px;text-align:center">
            <div style="width:72px;height:72px;background:linear-gradient(135deg,#2ecc71,#27ae60);border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin:0 auto 20px;font-size:32px;line-height:72px">
              &#10003;
            </div>
            <h1 style="color:#ffffff;font-size:24px;font-weight:800;margin:0 0 6px">Order Confirmed!</h1>
            <p style="color:rgba(255,255,255,0.65);font-size:14px;margin:0">Order <strong style="color:#a78bfa">#{order_id}</strong> is being processed</p>
          </td>
        </tr>

        <!-- GREETING -->
        <tr>
          <td style="padding:32px 40px 0">
            <p style="color:#1a1a2e;font-size:17px;font-weight:700;margin:0 0 8px">Thank you, {first}! &#127881;</p>
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 24px">
              Your order has been received and is now being prepared. We'll keep you updated as it moves through to delivery.
            </p>
          </td>
        </tr>

        <!-- ORDER SUMMARY -->
        <tr>
          <td style="padding:0 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1.5px solid #e2e8f0;border-radius:14px;overflow:hidden">
              <thead>
                <tr style="background:#f8fafc">
                  <th style="padding:12px 14px;text-align:left;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#94a3b8">Item</th>
                  <th style="padding:12px 14px;text-align:center;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#94a3b8">Qty</th>
                  <th style="padding:12px 14px;text-align:right;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#94a3b8">Total</th>
                </tr>
              </thead>
              <tbody>
                {rows}
                {discount_row}
                <tr style="background:#f8fafc">
                  <td colspan="2" style="padding:12px 14px;text-align:right;font-size:14px;font-weight:700;color:#1a1a2e">Order Total</td>
                  <td style="padding:12px 14px;text-align:right;font-size:18px;font-weight:900;color:#6C63FF">${total:.2f}</td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>

        <!-- CTA -->
        <tr>
          <td style="padding:32px 40px;text-align:center">
            <a href="{app_url}" style="display:inline-block;background:linear-gradient(135deg,#6C63FF,#5a52d5);color:#ffffff;text-decoration:none;padding:14px 40px;border-radius:12px;font-size:15px;font-weight:700;box-shadow:0 6px 22px rgba(108,99,255,0.4)">
              Track Your Order &nbsp;&#8594;
            </a>
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0;margin:0"></td></tr>
        <tr>
          <td style="padding:20px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:11px;margin:0">Group D · PROG315 — Limkokwing University, Sierra Leone · SDG 8</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    send_email(
        subject=f"Order #{order_id} Confirmed – Thank you, {first}!",
        html_body=html_body,
        recipient=customer_email,
    )


def send_seller_order_notification(
    seller_email: str,
    shop_name: str,
    customer_name: str,
    items: list,          # list of dicts: {name, qty, unit_price}
    order_id: int,
) -> None:
    """Notify a seller when a customer orders one of their products."""
    app_url     = os.getenv("APP_URL", "http://localhost:8000")
    first_shop  = shop_name.split()[0] if shop_name else "Shop"
    subtotal    = sum(i['unit_price'] * i['qty'] for i in items)

    rows = "".join(
        f"""<tr>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;color:#1a1a2e;font-size:14px"><strong>{item['name']}</strong></td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:center;color:#64748b;font-size:13px">x{item['qty']}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0f0f0;text-align:right;font-weight:700;color:#f39c12;font-size:14px">${item['unit_price']*item['qty']:.2f}</td>
        </tr>"""
        for item in items
    )

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Inter,-apple-system,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:580px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 40px rgba(0,0,0,0.10)">

        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#f39c12 0%,#e67e22 60%,#d35400 100%);padding:44px 40px 36px;text-align:center">
            <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px"><tr><td style="background:rgba(255,255,255,0.20);border:2px solid rgba(255,255,255,0.40);border-radius:16px;padding:11px 20px;font-size:15px;font-weight:900;color:#ffffff;font-family:'Segoe UI',Inter,sans-serif;letter-spacing:-0.3px">&#128722;&nbsp;EcomInventory Pro</td></tr></table>
            <h1 style="color:#fff;font-size:24px;font-weight:800;margin:0 0 6px">&#127881; New Order!</h1>
            <p style="color:rgba(255,255,255,0.85);font-size:14px;margin:0">
              <strong>{customer_name}</strong> just ordered from <strong>{shop_name}</strong>
            </p>
          </td>
        </tr>

        <!-- BODY -->
        <tr>
          <td style="padding:32px 40px 0">
            <p style="color:#1a1a2e;font-size:16px;font-weight:700;margin:0 0 6px">Order #{order_id}</p>
            <p style="color:#64748b;font-size:14px;line-height:1.75;margin:0 0 22px">
              A customer has placed an order for products from <strong style="color:#f39c12">{shop_name}</strong>.
              Log in to your dashboard to view and process the order.
            </p>
          </td>
        </tr>

        <!-- ITEMS -->
        <tr>
          <td style="padding:0 40px">
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1.5px solid #e2e8f0;border-radius:14px;overflow:hidden">
              <thead>
                <tr style="background:#fff8ed">
                  <th style="padding:11px 14px;text-align:left;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#b07d0a">Product</th>
                  <th style="padding:11px 14px;text-align:center;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#b07d0a">Qty</th>
                  <th style="padding:11px 14px;text-align:right;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#b07d0a">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {rows}
                <tr style="background:#fff8ed">
                  <td colspan="2" style="padding:12px 14px;text-align:right;font-size:13px;font-weight:700;color:#1a1a2e">Your Subtotal</td>
                  <td style="padding:12px 14px;text-align:right;font-size:18px;font-weight:900;color:#f39c12">${subtotal:.2f}</td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>

        <!-- CTA -->
        <tr>
          <td style="padding:32px 40px;text-align:center">
            <a href="{app_url}" style="display:inline-block;background:linear-gradient(135deg,#f39c12,#e67e22);color:#ffffff;text-decoration:none;padding:14px 40px;border-radius:12px;font-size:15px;font-weight:700;box-shadow:0 6px 22px rgba(243,156,18,0.4)">
              View in Dashboard &nbsp;&#8594;
            </a>
          </td>
        </tr>

        <!-- DIVIDER -->
        <tr><td style="padding:0 40px"><hr style="border:none;border-top:1px solid #e2e8f0;margin:0"></td></tr>
        <tr>
          <td style="padding:20px 40px;text-align:center">
            <p style="color:#94a3b8;font-size:11px;margin:0">Group D · PROG315 — Limkokwing University, Sierra Leone · SDG 8</p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    send_email(
        subject=f"New Order #{order_id} — {customer_name} ordered from {shop_name}",
        html_body=html_body,
        recipient=seller_email,
    )


def send_email(subject: str, html_body: str, recipient: str) -> None:
    # Hosts like Render block outbound SMTP ports on free plans, so prefer
    # Brevo's HTTPS API when a key is configured; SMTP remains the fallback.
    brevo_key = os.getenv("BREVO_API_KEY", "").strip()
    sender    = os.getenv("SMTP_USER", "")
    if brevo_key and sender and recipient:
        try:
            import httpx
            resp = httpx.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={"api-key": brevo_key, "content-type": "application/json"},
                json={
                    "sender": {"name": "EcomInventory Pro", "email": sender},
                    "to": [{"email": recipient}],
                    "subject": subject,
                    "htmlContent": html_body,
                },
                timeout=15,
            )
            if resp.status_code in (200, 201):
                print(f"[EMAIL] Sent OK via Brevo -> {recipient} | {subject}", flush=True)
                return
            print(
                f"[EMAIL ERROR] Brevo {resp.status_code}: {resp.text} — trying SMTP",
                flush=True,
            )
        except Exception as exc:
            print(f"[EMAIL ERROR] Brevo failed: {exc} — trying SMTP", flush=True)

    smtp_host     = os.getenv("SMTP_HOST", "")
    smtp_port     = int(os.getenv("SMTP_PORT", "587"))
    smtp_user     = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if not all([smtp_host, smtp_user, smtp_password, recipient]):
        print(
            f"[EMAIL] SMTP not configured — skipped ({recipient}) | "
            f"HOST={smtp_host!r} USER={smtp_user!r} PASS={'set' if smtp_password else 'MISSING'}",
            flush=True,
        )
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = recipient
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [recipient], msg.as_string())
        print(f"[EMAIL] Sent OK -> {recipient} | {subject}", flush=True)
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed -> {recipient} | {exc}", flush=True)
