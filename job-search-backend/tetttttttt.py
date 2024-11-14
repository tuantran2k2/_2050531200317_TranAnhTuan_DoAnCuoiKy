from controllers.crewai import _main

ans = _main._crewai_jobscv(1)


print(ans)

# from dependencies.dependencies import get_db
# from sqlalchemy.orm import Session
# from models import CV, BoSuuTap,KhachHang,LichSuTroChuyen,PhuongXa,QuanHuyen,QuyenTruyCap, ThonTo,TinhThanh,ViToken
# def get_cv(id_CV: int, db: Session):
#     cv = db.query(CV).filter(CV.maCV == id_CV).first()
#     if cv is None:
#         return None

#     cv_data = {
#         "maCV": cv.maCV,
#         "tenCV": cv.tenCV,
#         "Nganh": cv.Nganh,
#         "KyNangMem": cv.KyNangMem,
#         "KyNangChuyenNganh": cv.KyNangChuyenNganh,
#         "hocVan": cv.hocVan,
#         "tinhTrang": cv.tinhTrang,
#         "DiemGPA": cv.DiemGPA,
#         "soDienThoai": cv.soDienThoai,
#         "email": cv.email,
#         "diaChi": cv.diaChi,
#         "GioiThieu": cv.GioiThieu,
#         "maKH": cv.maKH,
#         "ChungChi": cv.ChungChi
#     }

#     return cv_data

# # Tạo một phiên làm việc của `Session`
# with next(get_db()) as db:
#     data = get_cv(1, db)
#     print(data)