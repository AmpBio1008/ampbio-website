# Ampbio Website

Static marketing website for **Ampbio** — specialised products and services across the biopharma lifecycle.

## Pages
| File | Page |
|------|------|
| `index.html` | Home |
| `products.html` | Products |
| `scientific-platforms.html` | Scientific Platforms |
| `research-development.html` | Research – Development |
| `consultancy-research-training.html` | Consultancy, Research & Training |
| `about.html` | About Ampbio |
| `connect.html` | Connect (contact form) |

## Stack
Plain HTML/CSS/JS — no build step. Shared `styles.css` (design-system classes) and `app.js` (header, mobile menu, scroll reveal, hero video). Fonts: D-DIN, IBM Plex Sans, IBM Plex Mono. Brand: navy `#0a1524`, amber `#FD9D05`, cream `#fdecdd`.

## Run locally
Any static server, e.g.:

```bash
python -m http.server 8000
# open http://localhost:8000
```

## Contact form
`connect.html` posts to [Web3Forms](https://web3forms.com) and emails enquiries to **bd@amps.bio**. Set your access key in the hidden `access_key` input (replace `PASTE_YOUR_WEB3FORMS_ACCESS_KEY_HERE`).

## Contact
bd@amps.bio · +91 96606 45155
