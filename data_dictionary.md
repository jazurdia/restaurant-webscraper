# Diccionario de Datos — Manhattan Reviews

Columnas principales y derivadas:

- **restaurant_name**: Nombre del restaurante.
  _Ejemplo_: Mission Ceviche
- **neighborhood**: Barrio en Manhattan asociado al restaurante.
  _Ejemplo_: Upper East Side
- **cuisine_type**: Tipo de cocina (si está disponible).
  _Ejemplo_: Peruvian
- **place_url**: URL del lugar en Google Maps.
  _Ejemplo_: https://www.google.com/maps/place/Mission+Ceviche/@40.7722267,-73.9567762,15.25z/data=!4m12!1m2!2m1!1sUpper+East+Side+restaurants!3m8!1s0x89c259a1b1cb7311:0xf3889e5221730682!8m2!3d40.7691005!4d-73.9578631!9m1!1b1!15sChtVcHBlciBFYXN0IFNpZGUgcmVzdGF1cmFudHNaHSIbdXBwZXIgZWFzdCBzaWRlIHJlc3RhdXJhbnRzkgETcGVydXZpYW5fcmVzdGF1cmFudJoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VOYWIyWnBRVWhCRUFFqgFVEAEqDyILcmVzdGF1cmFudHMoADIfEAEiG_KPfi-k_dVNgnKFMxu6E2RmvwNHx3TqlrWUWDIfEAIiG3VwcGVyIGVhc3Qgc2lkZSByZXN0YXVyYW50c-ABAPoBBAg_EEQ!16s%2Fg%2F11hyn1xw82?entry=ttu&g_ep=EgoyMDI1MTAwMS4wIKXMDSoASAFQAw%3D%3D
- **reviewer_name**: Nombre del usuario autor de la reseña.
  _Ejemplo_: Anonymous
- **rating**: Calificación numérica de 1 a 5.
  _Ejemplo_: 4.0
- **review_text**: Texto libre de la reseña.
  _Ejemplo_: Went on a date with someone who never had Peruvian before, she tells me she really liked it. I Found the food okay, I found the food lacking more flavour. The presentation was good, the atmosphere is great and the customer service was really good.
- **review_text_translated**: Texto traducido, si se dispone.
  _Ejemplo_: It's a unique place in upper Manhattan with special attention, and you don't have to go to Peru to enjoy its cuisine and warmth. Thank you, Luis, Carla, and Eduardo, especially, not to mention the other key players in this special restaurant.
- **review_length**: Longitud del texto de la reseña en caracteres.
  _Ejemplo_: 247
- **published_date**: Fecha de publicación en formato relativo (si se extrajo).
  _Ejemplo_: 2025-10-07T00:43:31.533Z
- **published_timestamp**: Marca de tiempo unix (s/ms).
  _Ejemplo_: 4 hours ago
- **likes_count**: Cantidad de 'me gusta' de la reseña.
  _Ejemplo_: 0
- **reviewer_total_reviews**: Reseñas totales del autor.
  _Ejemplo_: 24
- **is_local_guide**: Indicador booleano si es Local Guide.
  _Ejemplo_: True
- **owner_response**: Respuesta del propietario (si existe).
  _Ejemplo_: Hey Ian, 

Thank you for visiting us! We're happy to hear your date enjoyed the Peruvian cuisine. We appreciate your feedback on the flavors and will keep working on enhancing our dishes.

Looking forward to welcoming you back soon!

The Mission Ceviche Upper East Side Team
- **review_id**: ID único de la reseña (si existe).
- **review_url**: URL directa a la reseña.
- **review_datetime_utc**: Fecha-hora en UTC derivada del timestamp.
- **review_date**: Fecha (YYYY-MM-DD) derivada.
- **review_year**: Año de la reseña (derivado).
- **review_month**: Mes de la reseña (derivado).
- **neighborhood_norm**: Barrio normalizado (trim).
  _Ejemplo_: Upper East Side
- **neighborhood_canon**: Barrio mapeado a una taxonomía canónica simple.
  _Ejemplo_: Upper East Side