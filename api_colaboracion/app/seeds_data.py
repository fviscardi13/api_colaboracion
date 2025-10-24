from app.database import db
from app.models.ong_model import ONG
from app.models.project_model import Project
from app.models.request_model import Request

def init_app(app):
    with app.app_context():
        db.create_all()

        if ONG.query.first():
            print("Seeds ya cargados. Saltando inicialización.")
            return

        print("Cargando datos de prueba...")

        ong1 = ONG(
            name="ONG AyudaTotal",
            email="ayudatotal@ong.com",
            bonita_user="walter.bates"
        )
        ong1.set_password("1234")

        ong2 = ONG(
            name="ONG Futuro",
            email="futuro@ong.com",
            bonita_user="walter.bates"
        )
        ong2.set_password("abcd")


        db.session.add_all([ong1, ong2])
        db.session.commit()

        proyecto1 = Project(
            ong_id=ong1.id,
            name="Proyecto Salud",
            description="Mejoras en la clínica barrial",
            type="salud",
            country="Argentina",
            neighborhood="Palermo"
        )

        proyecto2 = Project(
            ong_id=ong2.id,
            name="Proyecto Educación",
            description="Donación de útiles escolares",
            type="educación",
            country="Argentina",
            neighborhood="Recoleta"
        )

        db.session.add_all([proyecto1, proyecto2])
        db.session.commit()

        pedido1 = Request(
            project_id=proyecto1.id,
            ong_id=ong1.id,
            type="materiales",
            description="Necesitamos insumos médicos básicos",
            amount=5000
        )

        pedido2 = Request(
            project_id=proyecto2.id,
            ong_id=ong2.id,
            type="materiales",
            description="Necesitamos libros y mochilas para 50 chicos",
            amount=2000
        )


        db.session.add_all([pedido1, pedido2])
        db.session.commit()

        print("Seeds cargados correctamente:")
        print("ONGs:", ONG.query.count())
        print("Proyectos:", Project.query.count())
        print("Pedidos:", Request.query.count())