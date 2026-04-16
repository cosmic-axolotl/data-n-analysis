import numpy as np
import matplotlib.pyplot as plt
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord

# ── 1. BAIXAR DADOS DO NGC 752 ────────────────────────────────────────────────
Vizier.ROW_LIMIT = -1

coord  = SkyCoord(ra=29.0, dec=37.8, unit=(u.deg, u.deg))
result = Vizier.query_region(coord, radius=1.0 * u.deg, catalog="J/A+A/618/A93")

table   = result['J/A+A/618/A93/members']
members = table[table['PMemb'] > 0.7]
print(f"Membros selecionados: {len(members)}")

# ── 2. CALCULAR MAGNITUDE ABSOLUTA ───────────────────────────────────────────
parallax = members['plx'].data
gmag     = members['Gmag'].data
bp_rp    = members['BP-RP'].data

mask     = parallax > 0
parallax = parallax[mask]
gmag     = gmag[mask]
bp_rp    = bp_rp[mask]

distance_pc  = 1000.0 / parallax
dist_modulus = 5 * np.log10(distance_pc / 10.0)
abs_gmag     = gmag - dist_modulus

print(f"Estrelas válidas: {len(abs_gmag)}")

# ── 3. CARREGAR ISOCRONA PARSEC ───────────────────────────────────────────────
def load_parsec_isochrone(filepath='isochrone_parsec.dat'):
    col_names = None
    data_rows = []

    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') and 'Gmag' in line:
                col_names = line.lstrip('#').split()
            elif not line.startswith('#') and line.strip():
                data_rows.append(line.split())

    if col_names is None:
        print("Cabeçalho não encontrado. Primeiras linhas:")
        with open(filepath, 'r') as f:
            for i, l in enumerate(f):
                print(l.rstrip())
                if i > 20:
                    break
        return None, None

    data      = np.array(data_rows, dtype=float)
    df        = {name: data[:, i] for i, name in enumerate(col_names)}
    bp_rp_iso = df['G_BPmag'] - df['G_RPmag']
    abs_g_iso = df['Gmag']

    print(f"Isocrona carregada: {len(abs_g_iso)} pontos")
    return bp_rp_iso, abs_g_iso

bp_rp_iso, abs_g_iso = load_parsec_isochrone('isochrone_parsec.dat')

# ── 4. PLOT ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 7))

scatter = ax.scatter(
    bp_rp, abs_gmag,
    c=bp_rp, cmap='RdYlBu_r',
    s=15, alpha=0.7, zorder=2,
    label='Membros NGC 752 (Gaia DR2)'
)

if bp_rp_iso is not None:
    ax.plot(
        bp_rp_iso, abs_g_iso,
        color='black', linewidth=1.5,
        linestyle='--', zorder=3,
        label='Isocrona PARSEC 1 Gyr (Z=0.019)'
    )

ax.annotate(
    'Gigantes\nvermelhas',
    xy=(1.1, 0.8), xytext=(0.3, -1.5),
    fontsize=9, color='darkred',
    arrowprops=dict(arrowstyle='->', color='darkred', lw=1.2)
)

ax.invert_yaxis()
ax.set_xlim(-0.5, 3.5)
ax.set_ylim(12, -4)

ax.set_xlabel('BP − RP  [mag]', fontsize=13)
ax.set_ylabel('$M_G$  [mag]', fontsize=13)
ax.set_title('Diagrama H-R — NGC 752', fontsize=15, fontweight='bold')

cbar = fig.colorbar(scatter, ax=ax, pad=0.02)
cbar.set_label('BP − RP  (azul = quente, vermelho = frio)', fontsize=11)

spectral_types = {
    'B': (-0.1, -0.5), 'A': (0.2, 2.0),
    'F': (0.5,  3.5),  'G': (0.8, 5.2),
    'K': (1.2,  7.0),  'M': (2.0, 10.0),
}
for sp, (x, y) in spectral_types.items():
    ax.annotate(sp, xy=(x, y), fontsize=9,
                color='gray', ha='center', style='italic')

ax.legend(fontsize=10, loc='upper left')
ax.grid(True, alpha=0.3, linestyle=':')
plt.tight_layout()

fig.savefig('hr_ngc752.pdf', dpi=300, bbox_inches='tight')
fig.savefig('hr_ngc752.png', dpi=150, bbox_inches='tight')
plt.show()
print("Salvo: hr_ngc752.pdf / .png")