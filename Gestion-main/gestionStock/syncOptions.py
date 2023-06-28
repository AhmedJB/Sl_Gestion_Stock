from controller.models import OptionCategories


names = {"eau":"Radiateur Eau","air":"Radiateur Air","clime":"Radiateur Clime","chauf":"Radiateur Chauffage","bonchon":"Bonchon","maneau":"Maneau","Deurite":"Deurite","antifel":"Antifèlle","fref":"Fréférant","termonstat":"Termonstat"}

values = [
    {
      "name": names["eau"],
      "value": "eau",
    },
    {
      "name": names["air"],
      "value": "air",
    },
    {
      "name": names["clime"],
      "value": "clime",
    },
    {
      "name": names["chauf"],
      "value": "chauf",
    },
    {
      "name": names["bonchon"],
      "value": "bonchon",
    }
    ,
    {
      "name": names["maneau"],
      "value": "maneau",
    }
    ,
    {
      "name": names["Deurite"],
      "value": "Deurite",
    }
    ,
    {
      "name": names["antifel"],
      "value": "antifel",
    }
    ,
    {
      "name": names["fref"],
      "value": "fref",
    }
    ,
    {
      "name": names["termonstat"],
      "value": "termonstat",
    }
  ]



def sync():
    for val in values:
        c = OptionCategories.objects.create(name=val['name'],value=val['value'])
        c.save()
    print("done")