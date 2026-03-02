# Navegación Espacial en Personas con Discapacidad Visual

## Descripcion del proyecto

Artículo de investigación empírica titulado **"Tacto y acciones corporales como claves de navegación espacial: Un estudio comparativo entre personas con discapacidad visual y personas videntes"**.

Estudio cuasi-experimental (diseño factorial mixto 2x2x2x4) que explora cómo la experticia en navegación no visual modula la ponderación e integración de distintas claves sensoriales (kinestésicas-vestibulares, táctiles y de acción) durante tareas de integración de trayectoria. Compara el desempeño de personas con discapacidad visual adquirida (DV, n=15) frente a personas videntes con ojos vendados (NDV, n=13) usando el paradigma de completación de triángulos.

## Afiliación institucional

- **Centro de investigación:** Centro de Investigaciones en Psicología, Cognición y Cultura, Universidad del Valle, Colombia.
- **Reclutamiento:** Hospital Universitario del Valle (HUV), Colombia.

## Revista objetivo

**Universitas Psychologica** — Pontificia Universidad Javeriana.
- Máximo 8000 palabras (incluyendo citas, tablas, figuras y referencias).
- Formato APA 7a edición.
- Resumen: 120-150 palabras (español e inglés).
- 3-6 palabras clave (cada una < 4 palabras).
- Fuente Times New Roman 12pt, interlineado 2.0, tamaño carta, márgenes 2.5cm.
- Figuras en archivos independientes (TIF/JPG/PNG, mínimo 300 dpi).

## Estructura del repositorio

```
├── CLAUDE.md                          # Este archivo
├── manuscrito/                        # Documento LaTeX
│   ├── main.tex                       # Archivo principal del manuscrito
│   ├── referencias.bib                # Bibliografía BibTeX
│   └── figuras/                       # Copias de figuras para compilación LaTeX
├── datos/                             # Datos experimentales
│   ├── datos 26_06_2024.xlsx          # Base de datos principal
│   ├── datos 26_06_2024 - copia.xlsx  # Copia de respaldo
│   ├── Modalidad_x_forma.xlsx         # Datos cruzados: modalidad × forma
│   ├── Modalidad_x_tamaño.xlsx        # Datos cruzados: modalidad × tamaño
│   └── Modalidad_sensorial.xlsx       # Datos por modalidad sensorial
├── analisis/                          # Scripts y productos del análisis
│   ├── analisis_completo.py           # Script Python del análisis estadístico
│   ├── resultados_completos.txt       # Output completo del análisis
│   ├── guia_resultados.md             # Guía de resultados para escritura
│   └── literatura_actualizada.md      # Literatura 2020-2025 compilada
├── figuras/                           # Figuras originales (PNG 300 dpi)
│   ├── fig1_interaction_CE_MS.png
│   ├── fig2_individual_trajectories.png
│   └── ...
└── docs_originales/                   # Versiones Word anteriores
    ├── Navegación ciegos.docx         # Versión principal (~julio 2025)
    ├── Navegación ciegos - abril 2025 - Mateo.docx
    ├── Criterios revista.docx         # Guía para autores de Universitas Psychologica
    └── Libro1.xlsx                    # Datos auxiliares
```

## Diseño experimental

### Variables independientes
- **Condición de experticia (CE):** DV (discapacidad visual adquirida) vs NDV (sin discapacidad visual) — factor inter-sujeto.
- **Organización por forma (OF):** Triángulos agudos (<45°) vs obtusos (>90°) — factor intra-sujeto.
- **Organización por tamaño (OT):** Distancia de retorno 2m vs 4m — factor intra-sujeto.
- **Modalidad sensorial (MS):** 4 niveles — factor intra-sujeto.
  1. Kinestésica-vestibular (sin objetos ni acciones, línea base)
  2. Tacto pasivo (tocar objetos sin usarlos)
  3. Interacción funcional (usar objetos)
  4. Control (acciones en el aire, sin objetos)

### Variables dependientes
- **Error de posición (EP):** Distancia en cm entre punto de origen y punto alcanzado por el participante.
- **Error de estimación angular:** Diferencia en grados entre dirección estimada y dirección ideal.

### Análisis estadístico
- Software: R (R Core Team, 2022).
- ANOVA de medidas repetidas 2x2x2x4 (modelo completo).
- ANOVA de medidas repetidas 2x4 (CE x MS, colapsando OF y OT).
- Comparaciones post hoc con ajuste de Bonferroni.

## Hallazgos principales

1. El grupo DV mostró mayor precisión y consistencia que el grupo NDV.
2. Interacción significativa CE x MS (F=5.10, p=.014, η²=0.164): la modalidad sensorial afecta diferencialmente a cada grupo.
3. El grupo NDV mejoró significativamente con claves táctiles y de acción, igualando al grupo DV.
4. La interacción funcional con objetos fue la condición con mayor precisión general (comparaciones Bonferroni: vs Kinestésica p=.006, vs Control p=.047).
5. La información geométrica (forma, tamaño) no produjo interacciones significativas de orden superior.
6. El error de estimación angular no mostró interacciones significativas entre grupos.

## Marco teórico clave

- Cognición corporeizada y extendida (Clark & Chalmers, 1998)
- Integración de trayectoria y mapas cognitivos (O'Keefe & Nadel, 1978; Dolins & Mitchell, 2010)
- Integración multisensorial bayesiana (Loomis et al., 2012)
- Adaptación sensorial y plasticidad funcional en personas con discapacidad visual
