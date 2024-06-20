# Avira Phantomvpn docker container

## Register:

https://campaigns.avira.com/en/crm/trial/prime-trial-3m

## Login first run:
```
phantomvpn_user="my.user@example.com" phantomvpn_pass="my.password" docker compose -f phantomvpn.yml up phantomvpn
```
## select server:
```
SERVER=us_nyc docker compose -f phantomvpn.yml up
```
### Server list:
```
nearest    Nearest location
au_per     Australia - Perth
au_syd     Australia - Sydney
at         Austria
be         Belgium
br         Brazil
bg         Bulgaria
ca         Canada
cl         Chile
cz         Czech Republic
dk         Denmark
fi         Finland
fr         France
de         Germany
gr         Greece
hk         Hong Kong
hu         Hungary
is         Iceland
ie         Ireland
il         Israel
it         Italy
jp         Japan
mx         Mexico
md         Moldova
nl         Netherlands
nz         New Zealand
no         Norway
pl         Poland
ro         Romania
rs         Serbia
sg         Singapore
si         Slovenia
es         Spain
se         Sweden
ch         Switzerland
gb_lon     United Kingdom - London
gb_mnc     United Kingdom - Manchester
us_atl     US - Atlanta
us_chi     US - Chicago
us_dal     US - Dallas
us_las     US - Las Vegas
us_lax     US - Los Angeles
us_mia     US - Miami
us_nyc     US - New York City
us_ewr     US - Newark
us_phx     US - Phoenix
us_sfo     US - San Francisco
us_sea     US - Seattle
us_stream  US - Streaming
us_was     US - Washington, D.C.
```
